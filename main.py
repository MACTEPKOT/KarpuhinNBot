import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils import executor
from handlers import register_handlers
from database import init_db

from config import API_TOKEN

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание объектов бота и диспетчера
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)

# Регистрация middleware
dp.middleware.setup(LoggingMiddleware())

# Инициализация базы данных
async def on_startup(dispatcher):
    await init_db()

if __name__ == '__main__':
    register_handlers(dp)
    executor.start_polling(dp, on_startup=on_startup)