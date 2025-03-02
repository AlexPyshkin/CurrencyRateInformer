import logging
import requests
import asyncio
import nest_asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Настройки
TOKEN = ""  # Замените на токен бота
CHAT_ID = ""  # Укажите ваш Telegram ID
EXCHANGE_RATE_URL = "https://www.cbr-xml-daily.ru/daily_json.js"  # API ЦБ РФ
EXCHANGE_RATE_URL2 = "https://api.nbrb.by/exrates/rates/451?periodicity=0"  # API ЦБ BY

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для получения курса евро
def get_euro_rate():
    try:
        response = requests.get(EXCHANGE_RATE_URL2)
        response.raise_for_status()
        data = response.json()
        # return data['Valute']['EUR']['Value']
        return data['Cur_OfficialRate']
    except Exception as e:
        logger.error(f"Ошибка получения курса: {e}")
        return None

# Функция отправки сообщения
async def send_rate():
    bot = Bot(token=TOKEN)
    rate = get_euro_rate()
    if rate:
        message = f"Текущий курс EUR: {rate:.2f} руб."
        await bot.send_message(chat_id=CHAT_ID, text=message)
    else:
        await bot.send_message(chat_id=CHAT_ID, text="Не удалось получить курс евро.")

# Обработчик команды /rate
async def rate_command(update: Update, context):
    rate = get_euro_rate()
    if rate:
        message = f"Текущий курс EUR: {rate:.2f} руб."
    else:
        message = "Не удалось получить курс евро."
    await update.message.reply_text(message)

# Запуск планировщика
async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_rate, "interval", hours=1)
    scheduler.start()
    logger.info("Бот запущен и проверяет курс каждый час.")
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("rate", rate_command))
    
    await app.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())