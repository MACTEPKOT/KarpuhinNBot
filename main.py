# Этап 1

# Дополнительный гайд по aiogram https://mastergroosha.github.io/aiogram-3-guide/quickstart/
# Дополнительный гайд по асинхронному бэкенду https://habr.com/ru/companies/kts/articles/598575/
# Дополнительный гайд по логированию https://habr.com/ru/companies/wunderfund/articles/683880/

# Установить библиотеки и фреймворки aiogram==3.4
# pip install aiogram
# pip install python-dotenv

# Для сохранения текущих пакетов в проекте и их версий при переносе используйте файл requirements.txt
# pip freeze — внешние пакеты проекта
# pip freeze > requirements.txt — сохранить внешние пакеты в файл
# pip install -r requirements.txt —  загрузить пакеты из файла


# импорты
import asyncio
from aiogram import Bot, Dispatcher, types
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def start():
    await dp.start_polling(bot)
# запуск бота через long_polling
if __name__ == "__main__":
    asyncio.run(start())

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode
from aiogram.utils import executor
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from dotenv import load_dotenv
from yadisk import YaDisk

load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
YANDEX_DISK_TOKEN = os.getenv('YANDEX_DISK_TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

Base = declarative_base()
engine = create_engine('sqlite:///database.db')
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    name = Column(String)
    teacher_id = Column(Integer, ForeignKey('users.id'))
    yadisk_token = Column(String)
    subscribed_teacher_id = Column(Integer, ForeignKey('users.id'))

class Folder(Base):
    __tablename__ = 'folders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    path = Column(String)
    last_modified = Column(String)

Base.metadata.create_all(engine)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    if not user:
        user = User(telegram_id=message.from_user.id, name=message.from_user.username)
        session.add(user)
        session.commit()
    await message.reply("Привет! Ты преподаватель или слушатель?", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("Преподаватель", "Слушатель"))

@dp.message_handler(Text(equals="Преподаватель"))
async def register_teacher(message: types.Message):
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    user.teacher_id = user.id
    session.commit()
    await message.reply("Вы зарегистрированы как преподаватель.")

@dp.message_handler(Text(equals="Слушатель"))
async def register_student(message: types.Message):
    await message.reply("Пожалуйста, введите ссылку-приглашение от преподавателя.")

@dp.message_handler(commands=['status'])
async def status(message: types.Message):
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    if user.yadisk_token:
        await message.reply(f"Ваш токен API Яндекс Диска: {user.yadisk_token}")
    else:
        await message.reply("У вас нет токена API Яндекс Диска. Пожалуйста, зарегистрируйтесь с помощью команды /register.")

@dp.message_handler(commands=['register'])
async def register(message: types.Message):
    await message.reply("Пожалуйста, следуйте инструкции по регистрации в API Яндекс Диска и получите токен. После этого используйте команду `/token` для проверки и сохранения вашего токена.")


@dp.message_handler(commands=['token'])
async def token(message: types.Message):
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    if user:
        await message.reply("Пожалуйста, отправьте ваш токен API Яндекс Диска.")

        @dp.message_handler(lambda msg: msg.text and len(msg.text) == 50)
        async def save_token(message: types.Message):
            user.yadisk_token = message.text
            session.commit()
            await message.reply("Токен успешно сохранен.")
    else:
        await message.reply("Пожалуйста, используйте команду /start для регистрации.")


@dp.message_handler(commands=['add'])
async def add_folder(message: types.Message):
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    if user and user.teacher_id:
        await message.reply(
            "Пожалуйста, отправьте путь к папке на Яндекс Диске, которую вы хотите добавить в отслеживаемые.")

        @dp.message_handler(lambda msg: msg.text and msg.text.startswith('/'))
        async def save_folder(message: types.Message):
            folder = Folder(user_id=user.id, path=message.text, last_modified=None)
            session.add(folder)
            session.commit()
            await message.reply("Папка успешно добавлена в отслеживаемые.")
    else:
        await message.reply("Вы не можете добавлять папки, так как не являетесь зарегистрированным преподавателем.")


@dp.message_handler(commands=['delete'])
async def delete_folder(message: types.Message):
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    if user and user.teacher_id:
        folders = session.query(Folder).filter_by(user_id=user.id).all()
        if folders:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for folder in folders:
                markup.add(folder.path)
            await message.reply("Выберите папку для удаления:", reply_markup=markup)

            @dp.message_handler(lambda msg: msg.text and msg.text.startswith('/'))
            async def confirm_delete(message: types.Message):
                folder = session.query(Folder).filter_by(user_id=user.id, path=message.text).first()
                if folder:
                    session.delete(folder)
                    session.commit()
                    await message.reply("Папка успешно удалена из отслеживаемых.")
                else:
                    await message.reply("Папка не найдена.")
        else:
            await message.reply("У вас нет отслеживаемых папок.")
    else:
        await message.reply("Вы не можете удалять папки, так как не являетесь зарегистрированным преподавателем.")