import re
import os
import datetime
import logging
import requests

from pyairtable import Table
from pyairtable.formulas import match
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, filters

AIRTABLE_ID = os.getenv('AIRTABLE_ID')
AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

table = Table(AIRTABLE_TOKEN, AIRTABLE_ID, 'flatmates')

START_ROUTES, END_ROUTES = range(2)
WHOIS_CLEANING, ADD_FLATMATE, FUCK_OFF = range(3)

wmo_to_text = [
    ([0],               '🌞 Чисте небо'),
    ([1, 2, 3],         '👻 Переважно ясно, похмуро'),
    ([45, 48],          '😶‍🌫️ Туман'),
    ([51, 53, 55],      '🌧 Мряка'),
    ([56, 57],          '🥶 Крижана мряка'),
    ([61, 63, 65],      '☔️ Дощ'),
    ([66, 67],          '🥶 Крижаний дощ'),
    ([71, 73, 75, 77],  '☃️ Снігопад'),
    ([80, 81, 82],      '💧Злива💧'),
    ([85, 86],          '❄️Сильний сніг❄️'),
    ([95],              '🌩 Можливо гроза'),
    ([96, 99],          '⚡️ Гроза'),
]

def get_war_stats():
    url = 'https://russianwarship.rip/api/v1/statistics/latest'
    r = requests.get(url)

    if r.status_code == 200:
        stats = r.json()['data']
        text = f"За сьогодні вмерло {stats['increase']['personnel_units']} русні, заголом здохло {stats['stats']['personnel_units']}"
    else:
        text = f'Нема інфи по русні - \n{r.status_code}{r.text}'
    return text

def get_forecast():
    url = 'https://api.open-meteo.com/v1/forecast/'
    params = {
        'latitude': '50.45',
        'longitude': '30.52',
        'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min', 'apparent_temperature_max', 'apparent_temperature_min'],
        'timezone': 'Europe/Berlin'
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        fc = r.json()['daily']
        weathercode = fc['weathercode'][0]
        max_temp = round(fc['temperature_2m_max'][0])
        min_temp = round(fc['temperature_2m_min'][0])
        feels_like_max = round(fc['apparent_temperature_max'][0])
        feels_like_min = round(fc['apparent_temperature_min'][0])

        for wmo in wmo_to_text:
            if weathercode in wmo[0]:
                weathercode = wmo[1]

        message = f'{weathercode}\nH:{max_temp}° L:{min_temp}°\n\nВідчувається:\nH:{feels_like_max}° L:{feels_like_min}°'    
    else:
        message = f'No weather data\n{r.status_code}{r.text}'

    return message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.username)
    keyboard = [
        [InlineKeyboardButton("🧻 Хто прибирає?", callback_data=str(WHOIS_CLEANING))],
        [InlineKeyboardButton("📝 Записатися на прибирання", callback_data=str(ADD_FLATMATE))],
        [InlineKeyboardButton("😘 Бот як ся маєш?", callback_data=str(FUCK_OFF))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привіт хозяїва! Я чорт тарас 😈 \n\n"
        "Що хочеш?", 
        reply_markup=reply_markup)
    return START_ROUTES

async def daily_routine(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send daily message based on weekday"""
    weekday = datetime.datetime.today().weekday()
    weekdays = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'Пʼятниця', 'Субота', 'Неділя']
    forecast = get_forecast()
    text = f'Привіт! Cьогодні {weekdays[weekday].lower()}!\n\n{forecast}'
    await context.bot.send_message(context.job.chat_id, text=text)

async def random_cat(update: Update, context:ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        caption='Хуйовий день? От тобі кіт для настрою!',
        photo=f'https://thiscatdoesnotexist.com/?ts={datetime.datetime.now()}')

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manually show daily message"""
    context.job_queue.run_once(daily_routine, 0, chat_id=update.effective_chat.id) #FIX ME
    await random_cat(update, context)

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    cleaner_record = table.first(formula=match({"isCleaning": True}))
    cleaner = cleaner_record['fields']['username']
    records = table.all(sort=['Created'])

    if cleaner == user.username:
        for idx, record in enumerate(records):
            if record == cleaner_record:
                new_cleaner_record = records[0] if len(records) == idx + 1 else records[idx + 1]
                new_cleaner = new_cleaner_record['fields']['username']
                table.update(new_cleaner_record['id'], {'isCleaning': True})
                table.update(cleaner_record['id'], {'isCleaning': False})
                await update.message.reply_text(f'Раб @{cleaner} каже що прибрався, але я б йому не вірив! Наступним хату прибирає @{new_cleaner}')
    else:
        await update.message.reply_text(f'@{user.username} ти нащо прибрався, зараз не твоя черга?\n\nКлятий москась @{cleaner}, ти чому пропустив свою чергу? Будеш прибирати на наступному тижні.')

async def add_flatmate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add flatmate to the Airtable."""
    text = ''
    flatmate = update.callback_query.from_user
    record = table.first(formula=match({"id": flatmate.id}))

    if record:
        text = f'@{flatmate.username} вже записаний до списку рабів цієї квартири.'
    else:
        table.create({'id': flatmate.id, 'username': flatmate.username})
        text = f'Записав @{flatmate.username} до рабів цієї квартири.'


    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def whois_cleaning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show flatmate who clean"""
    record = table.first(formula=match({"isCleaning": True}))
    username = record['fields']['username']
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Зараз черга @{username}')

async def fuck_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """f o"""
    flatmate = update.callback_query.from_user
    await context.bot.send_photo(
        chat_id=update.effective_chat.id, 
        caption=f'@{flatmate.first_name } іді нахуй',
        photo="https://s3-eu-central-1.amazonaws.com/hromadskeprod/pictures/files/000/032/877/original/05b6107d0a8b15719a4dcee9bc93bd1d.jpg?1504796052")

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Listen to key words and answer"""
    phrases = [
        (['+'], 'https://imgur.com/a/znlSLjw'),
        (['собака'], 'собакаааа, вона краще ніж ви люди, людям довіряти не можно, от собаки вони найкращі...'),
        (['чорт'], 'а що одразу чорт????'),
        (['пепсі'], 'кок кола краще'),
        (['кола'], 'пепсі краще'),
        (['так'], 'піздак'),
        (['бот'], 'а? що вже бот то?'),
        (['сало'], 'а борщ?'),
        (['борщ'], 'а сало?'),
        (['магазин', 'новус', 'сільпо', 'кишеня', 'фора'], 'купить мені пииииввааааа'),
        (['сука'], 'https://uk.wikipedia.org/wiki/%D0%9C%D1%96%D0%B7%D0%BE%D0%B3%D1%96%D0%BD%D1%96%D1%8F'),
        (['рашка'], 'не "рашка", а пидорахия блинолопатная скотоублюдия, свинособачий хуйлостан, рабские вымираты и нефтедырное пынебабве'),
        (['хозяйка', 'хозяйки', 'хозяйку'], 'Я піздолів, жополіз хозяйки, буду унітазом-мочеглотом. Хочу лізати волосату, немиту пізду під час її менструації. Якщо хозяйка трахалась — то тільки після ретельного митья. Хочу пити мочу і глотать всі виділення хозяйки. Вилижу жопу у анусі.'),
    ]

    message = re.findall(r'\b\S+\b|\+', str(update.message.text).lower())
    for phrase in phrases:
        for key in phrase[0]:
            if key in message:
                await update.message.reply_text(phrase[1])

async def forecast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show forecast"""
    await update.message.reply_text(get_forecast())

async def war_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show war stats"""
    await update.message.reply_text(get_war_stats())

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Answer to unknown command"""
    await update.message.reply_text('Що це за команда? Ти що дебіл?')

async def post_init(application: ApplicationBuilder) -> None:
    await application.bot.set_my_commands([
        ('start', 'Вітання та основні команди'),
        ('done', 'Я прибрався!'),
        ('whois_cleaning', 'Хто зараз прибирає?'),
        ('daily', 'Що там сьогодні?'),
        ('forecast', 'Прогноз погоди'),
        ('random_cat', 'Показати рандомну кітцю'),
        ('war_stats', 'Показати кількість мертвої русні'),
    ])

if __name__ == '__main__':
    logger.info("🖤 Flatmate Telegram Bot")
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(post_init).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(whois_cleaning, pattern="^" + str(WHOIS_CLEANING) + "$"),
                CallbackQueryHandler(add_flatmate, pattern="^" + str(ADD_FLATMATE) + "$"),
                CallbackQueryHandler(fuck_off, pattern="^" + str(FUCK_OFF) + "$"),
                # CallbackQueryHandler(four, pattern="^" + str(FOUR) + "$"),
            ],
            # END_ROUTES: [
                # CallbackQueryHandler(start_over, pattern="^" + str(ONE) + "$"),
                # CallbackQueryHandler(end, pattern="^" + str(TWO) + "$"),
            # ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.job_queue.run_daily(daily_routine, time=datetime.time(hour=8, minute=0), chat_id=TELEGRAM_CHAT_ID, name='daily_routine', days=(0,1,2,3,4,5,6))    

    reply_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, reply)
    done_handler = CommandHandler('done', done)
    daily_handler = CommandHandler('daily', daily)
    random_cat_handler = CommandHandler('random_cat', random_cat)
    forecast_handler = CommandHandler('forecast', forecast)
    war_stats_handler = CommandHandler('war_stats', war_stats)
    whois_cleaning_handler = CommandHandler('whois_cleaning', whois_cleaning)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(conv_handler)
    application.add_handler(reply_handler)
    application.add_handler(done_handler)
    application.add_handler(daily_handler)
    application.add_handler(random_cat_handler)
    application.add_handler(forecast_handler)
    application.add_handler(war_stats_handler)
    application.add_handler(whois_cleaning_handler)
    application.add_handler(unknown_handler)
    
    application.run_polling()