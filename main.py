from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram_dialog import setup_dialogs

from bot.dialogs.registration import router as start_router, start_dialog
from bot.dialogs.main_menu import router as menu_router, main_menu_dialog
from bot.handlers.commands import router as command_router
from configurations import get_config

config = get_config()

bot = Bot(token=config.bot_config.get_token(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


def main():
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(start_dialog)
    dp.include_router(main_menu_dialog)
    dp.include_router(command_router)
    setup_dialogs(dp)
    dp.run_polling(bot)


if __name__ == "__main__":
    main()
