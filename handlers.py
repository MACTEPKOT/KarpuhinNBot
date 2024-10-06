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
        status_message = f"Ваш статус: {user.role}"
        if user.token:
            status_message += f"\nВаш API токен: {user.token}"
        else:
            status_message += "\nУ вас нет токена, используйте /register для регистрации."
        await message.reply(status_message)
    else:
        await message.reply("Вы не зарегистрированы. Введите /register для начала.")


# Хендлер для команды /register
async def register_handler(message: types.Message):
    link = "https://oauth.yandex.ru/authorize?response_type=token&client_id=07ba5fa1577345a598fa9b898bfe05c3"
    await message.reply(
        f"Для регистрации перейдите по ссылке для получения токена Яндекс Диска: {link}. "
        "После получения токена используйте команду /token для его добавления."
    )


# Хендлер для команды /token
async def token_handler(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Пожалуйста, укажите токен после команды, например: /token ваш_токен")
        return

    token = args[1]
    user = await User.get_user_by_tg_id(message.from_user.id)
    if user:
        user.token = token
        await user.save()  # Убедитесь, что метод save() работает корректно
        await message.reply("Токен успешно добавлен.")
    else:
        await message.reply("Сначала зарегистрируйтесь с помощью команды /register.")


# Хендлер для команды /add
async def add_folder_handler(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Пожалуйста, укажите путь к папке после команды, например: /add /path/to/folder")
        return

    folder_path = args[1]
    user = await User.get_user_by_tg_id(message.from_user.id)
    if user and user.role == 'teacher':
        folder = Folder(path=folder_path, tg_user_id=user.tg_id)  # Измените на tg_user_id
        await folder.save()  # Убедитесь, что метод save() работает корректно
        await message.reply("Папка успешно добавлена для отслеживания.")
    else:
        await message.reply("Только преподаватели могут добавлять папки.")


# Хендлер для команды /delete
async def delete_folder_handler(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Пожалуйста, укажите путь к папке для удаления, например: /delete /path/to/folder")
        return

    folder_path = args[1]
    user = await User.get_user_by_tg_id(message.from_user.id)
    if user and user.role == 'teacher':
        folder = await Folder.get_by_path_and_user(folder_path, user.tg_id)  # Исправьте на tg_user_id
        if folder:
            await folder.delete()  # Убедитесь, что метод delete() работает корректно
            await message.reply("Папка успешно удалена из отслеживаемых.")
        else:
            await message.reply("Папка не найдена в вашем списке отслеживаемых.")
    else:
        await message.reply("Только преподаватели могут удалять папки.")


# Хендлер для команды /help
async def cmd_help(message: types.Message):
    help_text = (
        "Доступные команды:\n"
        "/start - Начать взаимодействие с ботом\n"
        "/register - Зарегистрироваться как преподаватель или слушатель\n"
        "/status - Проверить статус пользователя\n"
        "/token - Добавить токен API Яндекс Диска\n"
        "/add - Добавить папку на Яндекс Диске в отслеживаемые\n"
        "/delete - Удалить папку из отслеживаемых\n"
        "/help - Показать этот список команд"
    )
    await message.answer(help_text)


# Хендлер для команды /upload
async def upload_file_handler(message: types.Message):
    args = message.text.split()
    if len(args) < 3:
        await message.reply(
            "Пожалуйста, укажите путь к локальному файлу и удалённому пути, например: /upload /path/to/local/file /path/on/yandex/disk")
        return

    local_file_path = args[1]
    remote_folder_path = args[2]

    user = await User.get_user_by_tg_id(message.from_user.id)
    if user and user.token:
        client = YandexDiskClient(user.token)
        success = client.upload_file(local_file_path, remote_folder_path)
        if success:
            await message.reply("Файл успешно загружен.")
        else:
            await message.reply("Не удалось загрузить файл.")
    else:
        await message.reply("Сначала зарегистрируйтесь с помощью команды /register и добавьте токен.")


# Хендлер для команды /delete_file
async def delete_file_handler(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply(
            "Пожалуйста, укажите путь к удаляемому файлу, например: /delete_file /path/on/yandex/disk/file.txt")
        return

    remote_file_path = args[1]

    user = await User.get_user_by_tg_id(message.from_user.id)
    if user and user.token:
        client = YandexDiskClient(user.token)
        success = client.delete_file(remote_file_path)
        if success:
            await message.reply("Файл успешно удалён.")
        else:
            await message.reply("Не удалось удалить файл.")
    else:
        await message.reply("Сначала зарегистрируйтесь с помощью команды /register и добавьте токен.")


# Регистрация хендлеров
def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_handler, commands=['start'])
    dp.register_message_handler(status_handler, commands=['status'])
    dp.register_message_handler(register_handler, commands=['register'])
    dp.register_message_handler(token_handler, commands=['token'])
    dp.register_message_handler(add_folder_handler, commands=['add'])
    dp.register_message_handler(delete_folder_handler, commands=['delete'])
    dp.register_message_handler(upload_file_handler, commands=['upload'])  # Новый хендлер для загрузки файлов
    dp.register_message_handler(delete_file_handler, commands=['delete_file'])  # Новый хендлер для удаления файлов
    dp.register_message_handler(cmd_help, commands=['help'])