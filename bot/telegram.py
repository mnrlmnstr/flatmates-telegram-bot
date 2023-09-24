import re
import os
import mimetypes
import datetime
import logging
import random
from threading import Timer
from functools import wraps

from telegram import File, Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters

from bot.ai import generate_response
from bot.s3 import upload_file as s3_upload_file, list_files as s3_list_files, get_file_obj as s3_get_file_obj
from bot.translate import translate_text
from bot.weather import forecast_text
from bot.war_stats import get_war_stats, war_chart

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

reply_break = False
REPLY_BREAK_DURATION = 120
REPLY_PHRASES = [
    (['собака'], 'собакаааа, вона краще ніж ви люди, людям довіряти не можно, от собаки вони найкращі...'),
    (['чорт'], 'а що одразу чорт????'),
    (['бот'], 'а? що вже бот то?'),
    (['пепсі'], 'кок кола краще'),
    (['кола'], 'пепсі краще'),
    (['слава україні', 'слава украине'], 'Героям Слава!'),
    (['так'], 'піздак'),
    (['сало'], 'а борщ?'),
    (['борщ'], 'а сало?'),
    (['згодна, згоден'], 'з чим? ти ж дурна людина, тобі далеко до робота'),
    (['магазин', 'новус', 'сільпо', 'кишеня', 'фора'], 'купить мені пииииввааааа'),
    (['сука'], 'https://uk.wikipedia.org/wiki/%D0%9C%D1%96%D0%B7%D0%BE%D0%B3%D1%96%D0%BD%D1%96%D1%8F'),
    (['рашка'], 'не "рашка", а пидорахия блинолопатная скотоублюдия, свинособачий хуйлостан, '
                'рабские вымираты и нефтедырное пынебабве'),
    (['хозяйка', 'хозяйки', 'хозяйку'], 'Я піздолів, жополіз хозяйки, буду унітазом-мочеглотом. Хочу лізати '
                                        'волосату, немиту пізду під час її менструації. Якщо хозяйка трахалась — '
                                        'то тільки після ретельного митья. Хочу пити мочу і глотать всі виділення '
                                        'хозяйки. Вилижу жопу у анусі.'),
]

MESSAGE_BUFFER_SIZE = 1
messages_buffer = []


def disable_break():
    global reply_break
    reply_break = False
    logger.info('Reply break: OFF')


def enable_break():
    global reply_break
    if not reply_break:
        reply_break = True
        logger.info('Reply break: ON')
        Timer(REPLY_BREAK_DURATION, disable_break).start()


def restricted_to_chat(func):
    """Restrict usage of func to allowed chat only"""
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        chat_id = update.effective_chat.id
        if str(chat_id) != str(TELEGRAM_CHAT_ID):
            await context.bot.send_message(chat_id, text='Іди нахуй, ці команди тіки для хозяїв!')
            return
        return await func(update, context, *args, **kwargs)
    return wrapped


def digest_text():
    """Digest message based on weekday"""
    WEEKDAY = datetime.datetime.today().weekday()
    weekdays = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'Пʼятниця', 'Субота', 'Неділя']
    return f'{weekdays[WEEKDAY]}.\n\n{get_war_stats()} \n\n{forecast_text()}'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: Welcome message"""
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.username)
    await update.message.reply_text("Привіт хозяїва! Я чорт тарас 😈 \n\n"
                                    "Дивись команди у меню команд.")


async def morning(context: ContextTypes.DEFAULT_TYPE):
    """Callback that show digest at morning"""
    text = 'Добрий ранок! 🫠\n\n' + digest_text()
    await context.bot.send_message(context.job.chat_id, text=text)


async def digest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: show digest message and random cat"""
    WEEKDAY = datetime.datetime.today().weekday()

    await context.bot.send_message(update.effective_chat.id, text=digest_text())

    if WEEKDAY == 6:
        war_chart()
        tmp_dir = os.path.join(ROOT_DIR, 'tmp')
        photo = tmp_dir + '/war_chart.png'
        await update.message.reply_photo(photo=photo)


# TODO: Refactor 0(n+) in phrases
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Listen to every chat message and reply with phrase or photo"""

    reply_message = update.message.reply_to_message
    is_reply = reply_message and context.bot.first_name == reply_message.from_user.first_name

    if re.findall(r'чорт|тарас', str(update.message.text).lower()) or is_reply:
        message = translate_text(update.message.text, 'en')
        global messages_buffer
        if len(messages_buffer) == MESSAGE_BUFFER_SIZE:
            del messages_buffer[0]

        messages_buffer.append({'role' :'user', 'content': message})
        openai_reply = generate_response(messages_buffer)
        messages_buffer.append({'role' :'assistant', 'content': openai_reply})
        translated_reply = translate_text(openai_reply)
        await update.message.reply_text(translated_reply)
        return

    if re.findall(r'ы|ё|ъ|э', str(update.message.text).lower()):
        await update.message.reply_text('🚨🚨🚨 КАЦАП ДЕТЕКТЕД 🚨🚨🚨')

    if reply_break:
        return

    if random.random() > 0.01:
        return

    for phrase in REPLY_PHRASES:
        for key in phrase[0]:
            if re.match(r'^\b\S+\b$', key):
                message = re.findall(r'\b\S+\b', str(update.message.text).lower())
                if key in message:
                    await update.message.reply_text(phrase[1])
                    enable_break()
                    return
            elif re.search(key, update.message.text, re.IGNORECASE) and not re.match(r'^\b\S+\b$', key):
                await update.message.reply_text(phrase[1])
                enable_break()
                return

    files = s3_list_files('flatmatebot')
    index = random.randrange(0, len(files))
    photo = s3_get_file_obj(files[index]['key'])['Body'].read()
    await update.message.reply_photo(photo=photo, reply_to_message_id=update.message.id)
    enable_break()
    return


async def clean_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global messages_buffer
    if messages_buffer:
        await update.message.reply_text('Історія стерта: \n\n')
        messages_buffer = []
    else:
        await update.message.reply_text('Нічого нема')


@restricted_to_chat
async def add_meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Відправ мені міміс, щоб зберегти до колекції.')
    return 1


async def add_meme_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Спробуй команду знов чи відʼїбись.')
    return ConversationHandler.END


async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attachment = update.message.effective_attachment
    if isinstance(attachment, list):
        attachment = attachment[-1]

    if attachment.file_size > 20 * 1024 * 1024:
        await update.message.reply_html('Завелеку картинку суєш, хлопче.')
        return

    file = await attachment.get_file()

    def get_original_file_name():
        original_file_name = os.path.basename(file.file_path)
        if hasattr(attachment, 'file_name'):
            original_file_name = attachment.file_name
        return original_file_name

    file_name = get_original_file_name()
    mime_type = mimetypes.MimeTypes().guess_type(file_name)[0]

    tmp_dir = os.path.join(ROOT_DIR, 'tmp')
    if not os.path.isdir(tmp_dir):
        os.mkdir(tmp_dir)

    tmp_file_name = os.path.join(tmp_dir, str(datetime.datetime.timestamp(datetime.datetime.now())))
    file = await File.download_to_drive(file, tmp_file_name)
    s3_upload_file(file, 'flatmatebot', file_name, mime_type, 'public-read')
    try:
        os.unlink(tmp_file_name)
    except Exception as e:
        logger.error(e)
    await update.message.reply_text(text='Зберіг!')
    return ConversationHandler.END


async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = context.args
        if len(text[0]) == 2 and text[1]: # lazy, check for coutry codes x)
            target_lang = text[0]
            del text[0]
        else:
            target_lang = 'uk'

        text = ' '.join(text)
        translated_text = translate_text(text, target_lang)
        await update.message.reply_text(translated_text)
    except (IndexError, ValueError):
        await update.message.reply_text('А де текст?')


async def forecast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: show forecast"""
    await update.message.reply_text(forecast_text())


async def war_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: show war stats"""
    await update.message.reply_text(get_war_stats())



async def chat_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: show chat information"""
    await update.message.reply_text(f'chat_id: {update.effective_chat.id}')


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: answer to unknown command"""
    await update.message.reply_text('Що це за команда? Ти що дебіл?')


async def post_init(application: ApplicationBuilder) -> None:
    await application.bot.set_my_commands([
        ('start', 'Вітання!'),
        ('add_meme', 'Поповнити мемапедію Тараса'),
        ('digest', 'Що там сьогодні?'),
        ('forecast', 'Прогноз погоди'),
        ('random_cat', 'Показати рандомну кітцю'),
        ('war_stats', 'Показати кількість мертвої русні'),
        ('clean_history', 'Очистити останні 10 повідомлень з тарасом'),
    ])


def main():
    logger.info("🖤 Taras Bot")
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(post_init).build()

    add_meme_conv = ConversationHandler(
        entry_points=[CommandHandler('add_meme', add_meme)],
        states={
            1: [MessageHandler(filters.PHOTO, image_handler)]
        },
        fallbacks=[MessageHandler(filters.TEXT, add_meme_done)],
        per_user=True,
    )

    # Show digest at every morning 9:00 utc
    application.job_queue.run_daily(morning, time=datetime.time(hour=9, minute=0), chat_id=TELEGRAM_CHAT_ID,
                                    name='morning message', days=(0, 1, 2, 3, 4, 5, 6))

    reply_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, reply)
    digest_handler = CommandHandler('digest', digest)
    forecast_handler = CommandHandler('forecast', forecast)
    war_stats_handler = CommandHandler('war_stats', war_stats)
    chat_info_handler = CommandHandler('chat_info', chat_info)
    translate_handler = CommandHandler('translate', translate)
    clean_history_handler = CommandHandler('clean_history', clean_history)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(add_meme_conv)
    application.add_handler(reply_handler)
    application.add_handler(translate_handler)
    application.add_handler(clean_history_handler)
    application.add_handler(digest_handler)
    application.add_handler(forecast_handler)
    application.add_handler(war_stats_handler)
    application.add_handler(chat_info_handler)
    application.add_handler(unknown_handler)

    application.run_polling()
