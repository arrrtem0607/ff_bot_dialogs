from aiogram import types, Dispatcher, Bot, Router
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram_dialog import setup_dialogs
from aiogram_dialog import DialogManager, StartMode

from bot.dialogs.registration import start_dialog
from bot.utils.statesform import Registration
from configurations import get_config

config = get_config()

bot = Bot(token=config.bot_config.get_token(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()


@router.message(CommandStart())
async def command_start_process(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=Registration.get_first_name, mode=StartMode.RESET_STACK)


def main():
    dp.include_router(router)
    dp.include_router(start_dialog)
    setup_dialogs(dp)
    dp.run_polling(bot)


if __name__ == "__main__":
    main()
