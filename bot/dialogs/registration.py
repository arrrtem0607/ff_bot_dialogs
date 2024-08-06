import json
from functools import partial
from pathlib import Path
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, Row, Group
from aiogram_dialog.widgets.text import Const, Format, Multi
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput

from bot.utils.statesform import Registration, MainMenu
from bot.utils.validators import validate_name, validate_bank_name, validate_payment_details, validate_phone_number

router = Router()
DATA_FILE = Path("user_data.json")


def read_user_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def write_user_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# Handlers for success and error scenarios
async def on_success(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, value: str):
    dialog_manager.current_context().dialog_data[widget.widget_id] = value
    await dialog_manager.next()


async def on_error(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, error: Exception):
    await message.answer(text=f"⚠️ Ошибка: {str(error)}")


async def get_values(dialog_manager: DialogManager, keys: list, **kwargs):
    data = {key: dialog_manager.current_context().dialog_data.get(key, "") for key in keys}
    return data


async def review_getter(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.current_context().dialog_data
    return {
        "first_name_input": data.get("first_name_input", ""),
        "second_name_input": data.get("second_name_input", ""),
        "number_input": data.get("number_input", ""),
        "payment_details_input": data.get("payment_details_input", ""),
        "bank_name_input": data.get("bank_name_input", "")
    }


# Callback handlers for changing data
async def change_first_name(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(Registration.get_first_name, mode=StartMode.RESET_STACK)


async def change_second_name(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(Registration.get_second_name, mode=StartMode.RESET_STACK)


async def change_number(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(Registration.get_number, mode=StartMode.RESET_STACK)


async def change_payment_details(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(Registration.get_payment_details, mode=StartMode.RESET_STACK)


async def change_bank_name(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(Registration.get_bank_name, mode=StartMode.RESET_STACK)


async def confirm_data(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_id = str(c.from_user.id)
    user_data = read_user_data()
    dialog_data = dialog_manager.current_context().dialog_data

    # Сохранение данных пользователя
    user_data[user_id] = {
        "first_name": dialog_data.get("first_name_input"),
        "second_name": dialog_data.get("second_name_input"),
        "phone_number": dialog_data.get("number_input"),
        "payment_details": dialog_data.get("payment_details_input"),
        "bank_name": dialog_data.get("bank_name_input"),
        "role": "unapproved",  # роль будет назначена администратором позже
        "hourly_rate": 0  # ставка будет назначена администратором позже
    }
    write_user_data(user_data)

    await c.message.answer("✅ Ваши данные успешно сохранены! Ваша заявка отправлена на рассмотрение администратору.")
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
                Button(Const("✏️ Изменить фамилию"), id="change_second_name", on_click=change_second_name),
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
