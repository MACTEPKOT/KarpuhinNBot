from aiogram import types
from aiogram.dispatcher import Dispatcher
from models import User, Folder
from yadisk_client import YandexDiskClient

# Хендлер для команды /start
async def start_handler(message: types.Message):
    await message.reply("Добро пожаловать! Вы преподаватель или слушатель? Используйте /register для регистрации.")

# Хендлер для команды /status
async def status_handler(message: types.Message):
    user = await User.get_user_by_tg_id(message.from_user.id)
    if user:
        await message.reply(f"Ваш статус: {user.role}")
        if user.token:
            await message.reply(f"Ваш API токен: {user.token}")
        else:
            await message.reply("У вас нет токена, используйте /register для регистрации.")
    else:
        await message.reply("Вы не зарегистрированы. Введите /start для начала.")

# Хендлер для команды /register
async def register_handler(message: types.Message):
    await message.reply("Перейдите по ссылке для получения токена Яндекс Диска: <ссылка>. Используйте /token для добавления токена.")

# Хендлер для команды /token
async def token_handler(message: types.Message):
    token = message.text.split()[1]
    user = await User.get_user_by_tg_id(message.from_user.id)
    if user:
        user.token = token
        await user.save()
        await message.reply("Токен успешно добавлен.")
    else:
        await message.reply("Сначала зарегистрируйтесь с помощью команды /register.")

# Хендлер для команды /add
async def add_folder_handler(message: types.Message):
    folder_path = message.text.split()[1]
    user = await User.get_user_by_tg_id(message.from_user.id)
    if user and user.role == 'teacher':
        folder = Folder(path=folder_path, user_id=user.id)
        await folder.save()
        await message.reply("Папка успешно добавлена для отслеживания.")
    else:
        await message.reply("Только преподаватели могут добавлять папки.")

# Регистрация хендлеров
def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_handler, commands=['start'])
    dp.register_message_handler(status_handler, commands=['status'])
    dp.register_message_handler(register_handler, commands=['register'])
    dp.register_message_handler(token_handler, commands=['token'])
    dp.register_message_handler(add_folder_handler, commands=['add'])
