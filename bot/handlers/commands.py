import json
from pathlib import Path
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram_dialog import DialogManager, StartMode

from bot.utils.statesform import Registration, MainMenu

DATA_FILE = Path("user_data.json")

router = Router()


def read_user_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def write_user_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@router.message(CommandStart())
async def command_start(message: Message, dialog_manager: DialogManager):
    user_id = str(message.from_user.id)
    user_data = read_user_data()

    if user_id in user_data:
        # Если пользователь зарегистрирован, перенаправляем в главное меню
        await dialog_manager.start(state=MainMenu.main, mode=StartMode.RESET_STACK)
    else:
        # Если пользователь не зарегистрирован, перенаправляем в диалог регистрации
        await dialog_manager.start(state=Registration.get_first_name, mode=StartMode.RESET_STACK)


@router.message(Command("help"))
async def command_help(message: Message):
    await message.answer("ℹ️ Команды:\n/start - Начать работу\n/help - Помощь")
