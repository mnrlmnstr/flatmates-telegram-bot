import re
import os
# import datetime
import logging

from pyairtable import Table
from pyairtable.formulas import match
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_ID = os.getenv("AIRTABLE_ID")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

table = Table(AIRTABLE_TOKEN, AIRTABLE_ID, 'flatmates')

START_ROUTES, END_ROUTES = range(2)
WHOIS_CLEANING, ADD_FLATMATE, FUCK_OFF = range(3)

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

# async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Send the alarm message."""
#     job = context.job
#     await context.bot.send_message(job.chat_id, text=f"Beep! {job.data} seconds are over!")

# async def set_alarm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     now = datetime.datetime.now()
#     delta = datetime.timedelta(seconds=10)
#     time = now + delta
#     context.job_queue.run_once(alarm, time, chat_id=update.effective_chat.id, name=str(update.effective_chat.id), data=time)

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

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Answer to unknown command"""
    await update.message.reply_text('Що це за команда? Ти що дебіл?')

async def post_init(application: ApplicationBuilder) -> None:
    await application.bot.set_my_commands([
        ('start', 'Вітання та основні команди'),
        ('done', 'Я прибрався!'),
        ('whois_cleaning', 'Хто зараз прибирає?'),
    ])

if __name__ == '__main__':
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

    reply_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, reply)
    done_handler = CommandHandler('done', done)
    whois_cleaning_handler = CommandHandler('whois_cleaning', whois_cleaning)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    # application.add_handler(CommandHandler('alarm', alarm))
    # application.add_handler(CommandHandler('set_alarm', set_alarm))
    application.add_handler(conv_handler)
    application.add_handler(reply_handler)
    application.add_handler(done_handler)
    application.add_handler(whois_cleaning_handler)
    application.add_handler(unknown_handler)
    
    application.run_polling()