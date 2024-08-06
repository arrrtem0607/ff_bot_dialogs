from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Group, Row
from aiogram_dialog.widgets.text import Const

from bot.utils.statesform import MainMenu
from bot.utils.roles import UserRole

router = Router()


async def get_role(dialog_manager: DialogManager, **kwargs):
    role = dialog_manager.current_context().dialog_data.get("role", UserRole.PACKER)
    return {"role": role.value}


async def on_role_select(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    role = button.widget_id
    dialog_manager.current_context().dialog_data["role"] = role
    await dialog_manager.switch_to(MainMenu.main)


async def packer_menu(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(MainMenu.packer_menu)


async def administrator_menu(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(MainMenu.administrator_menu)


async def manager_menu(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(MainMenu.manager_menu)

main_menu_dialog = Dialog(
    Window(
        Const("Выберите свою роль:"),
        Group(
            Row(
                Button(Const("Упаковщик"), id="packer", on_click=on_role_select),
                Button(Const("Администратор"), id="administrator", on_click=on_role_select),
                Button(Const("Менеджер"), id="manager", on_click=on_role_select),
            ),
        ),
        state=MainMenu.main,
    ),
    Window(
        Const("Главное меню для упаковщика"),
        Button(Const("Начать упаковку"), id="start_packing", on_click=packer_menu),
        state=MainMenu.packer_menu,
    ),
    Window(
        Const("Главное меню для администратора"),
        Button(Const("Управление пользователями"), id="manage_users", on_click=administrator_menu),
        state=MainMenu.administrator_menu,
    ),
    Window(
        Const("Главное меню для менеджера"),
        Button(Const("Просмотр отчетов"), id="view_reports", on_click=manager_menu),
        state=MainMenu.manager_menu,
    )
)