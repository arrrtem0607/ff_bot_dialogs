import logging
from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram_dialog import setup_dialogs

from bot.dialogs.registration import router as start_router, start_dialog
from bot.dialogs.main_menu import router as menu_router, main_menu_dialog
from configurations import get_config
from database.entities.core import Database
from database.controllers.ORM import ORMController
from bot.middlewares.role import AccessMiddleware

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = get_config()

db = Database()
orm_controller = ORMController(db)

bot = Bot(token=config.bot_config.get_token(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def on_startup():
    logger.info("Starting up...")
    await orm_controller.create_tables()
    logger.info("Startup complete.")


def main():
    logger.info("Initializing main function...")
    dp.message.middleware(AccessMiddleware(allowed_roles=["admin", "packer", "manager", "loader"]))
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(start_dialog)
    dp.include_router(main_menu_dialog)
    setup_dialogs(dp)
    dp.startup.register(on_startup)
    logger.info("Running polling...")
    dp.run_polling(bot)


if __name__ == "__main__":
    main()
