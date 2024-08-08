import logging
from functools import partial

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, Row, Group
from aiogram_dialog.widgets.text import Const, Format, Multi
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput

from bot.utils.statesform import Registration, MainMenu
from bot.utils.validators import validate_name, validate_bank_name, validate_payment_details, validate_phone_number
from database.controllers.ORM import ORMController

logger = logging.getLogger(__name__)

router = Router()

# ORM Controller instance
orm_controller = ORMController()


# Handlers for success and error scenarios
async def on_success(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, value: str):
    logger.info(f"Validation success for widget {widget.widget_id}: {value}")
    dialog_manager.current_context().dialog_data[widget.widget_id] = value
    await dialog_manager.next()


async def on_error(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, error: Exception):
    logger.error(f"Validation error for widget {widget.widget_id}: {error}")
    await message.answer(text=f"⚠️ Ошибка: {str(error)}")


async def get_values(dialog_manager: DialogManager, keys: list, **kwargs):
    data = {key: dialog_manager.current_context().dialog_data.get(key, "") for key in keys}
    logger.debug(f"get_values data: {data}")
    return data


async def review_getter(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.current_context().dialog_data
    logger.debug(f"review_getter data: {data}")
    return {
        "first_name_input": data.get("first_name_input", ""),
        "second_name_input": data.get("second_name_input", ""),
        "number_input": data.get("number_input", ""),
        "payment_details_input": data.get("payment_details_input", ""),
        "bank_name_input": data.get("bank_name_input", "")
    }


# Callback handlers for changing data
async def change_first_name(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    logger.info("Changing first name.")
    await dialog_manager.start(Registration.get_first_name, mode=StartMode.RESET_STACK)


async def change_second_name(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    logger.info("Changing second name.")
    await dialog_manager.start(Registration.get_second_name, mode=StartMode.RESET_STACK)


async def change_number(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    logger.info("Changing number.")
    await dialog_manager.start(Registration.get_number, mode=StartMode.RESET_STACK)


async def change_payment_details(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    logger.info("Changing payment details.")
    await dialog_manager.start(Registration.get_payment_details, mode=StartMode.RESET_STACK)


async def change_bank_name(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    logger.info("Changing bank name.")
    await dialog_manager.start(Registration.get_bank_name, mode=StartMode.RESET_STACK)


async def confirm_data(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    logger.info("Confirming data.")
    data = dialog_manager.current_context().dialog_data
    worker_data = {
        "first_name": data.get("first_name_input"),
        "second_name": data.get("second_name_input"),
        "phone_number": data.get("number_input"),
        "payment_details": data.get("payment_details_input"),
        "bank_name": data.get("bank_name_input"),
        "role": "pending",  # Initial role is pending
        "tg_id": c.from_user.id,
        "status": "pending"
    }
    await orm_controller.create_worker(worker_data)
    await c.message.answer("✅ Ваши данные успешно сохранены!")
    await dialog_manager.start(MainMenu.main, mode=StartMode.RESET_STACK)

start_dialog = Dialog(
    Window(
        Multi(
            Const('👋 Привет!\n'),
            Const('Добро пожаловать на наш фулфилмент! Для начала работы нам нужно немного информации.\n'),
            Const('Давайте познакомимся! Пожалуйста, введите ваше имя:'),
            sep='\n'
        ),
        TextInput(id='first_name_input',
                  type_factory=validate_name,
                  on_success=on_success,
                  on_error=on_error),
        state=Registration.get_first_name,
    ),
    Window(
        Multi(
            Format('Приятно познакомиться, {first_name_input}! 😊'),
            Const('Теперь введите вашу фамилию:'),
            sep='\n'
        ),
        TextInput(id='second_name_input',
                  type_factory=validate_name,
                  on_success=on_success,
                  on_error=on_error),
        getter=partial(get_values, keys=["first_name_input"]),
        state=Registration.get_second_name,
    ),
    Window(
        Multi(
            Format('Отлично, {first_name_input} {second_name_input}! 📞'),
            Const('Теперь, пожалуйста, введите ваш номер телефона для связи:'),
            sep='\n'
        ),
        TextInput(id='number_input',
                  type_factory=validate_phone_number,
                  on_success=on_success,
                  on_error=on_error),
        getter=partial(get_values, keys=["first_name_input", "second_name_input"]),
        state=Registration.get_number,
    ),
    Window(
        Multi(
            Format('Отлично, {first_name_input} {second_name_input}! 💳'),
            Const('Введите реквизиты для выплаты заработной платы (номер банковской карты или номер телефона):'),
            sep='\n'
        ),
        TextInput(id='payment_details_input',
                  type_factory=validate_payment_details,
                  on_success=on_success,
                  on_error=on_error),
        getter=partial(get_values, keys=["first_name_input", "second_name_input"]),
        state=Registration.get_payment_details,
    ),
    Window(
        Multi(
            Format('Отлично, {first_name_input} {second_name_input}! 🏦'),
            Const('Введите название вашего банка:'),
            sep='\n'
        ),
        TextInput(id='bank_name_input',
                  type_factory=validate_bank_name,
                  on_success=on_success,
                  on_error=on_error),
        getter=partial(get_values, keys=["first_name_input", "second_name_input", "payment_details_input"]),
        state=Registration.get_bank_name,
    ),
    Window(
        Multi(
            Format('Пожалуйста, проверьте ваши данные:\n'
                   '👤 Имя: {first_name_input}\n'
                   '👥 Фамилия: {second_name_input}\n'
                   '📞 Номер телефона: {number_input}\n'
                   '💳 Реквизиты для оплаты: {payment_details_input}\n'
                   '🏦 Название банка: {bank_name_input}\n'),
            sep='\n'
        ),
        Group(
            Row(
                Button(Const("✏️ Изменить имя"), id="change_first_name", on_click=change_first_name),
                Button(Const("✏️ Изменить фамилию"), id="change_second_name"),
            ),
            Row(
                Button(Const("✏️ Изменить номер"), id="change_number", on_click=change_number),
                Button(Const("✏️ Изменить реквизиты"), id="change_payment_details", on_click=change_payment_details),
            ),
            Row(
                Button(Const("✏️ Изменить банк"), id="change_bank_name", on_click=change_bank_name),
                Button(Const("✅ Подтвердить данные"), id="confirm_data", on_click=confirm_data),
            ),
        ),
        getter=review_getter,
        state=Registration.review_data,
    ),
)


@router.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    user_id = message.from_user.id
    user_data = await orm_controller.get_worker_by_tg_id(user_id)
    if user_data:
        logger.info(f"User {user_id} is registered, navigating to main menu.")
        await dialog_manager.start(state=MainMenu.main, mode=StartMode.RESET_STACK)
    else:
        logger.info(f"User {user_id} is not registered, starting registration.")
        await dialog_manager.start(state=Registration.get_first_name, mode=StartMode.RESET_STACK)
