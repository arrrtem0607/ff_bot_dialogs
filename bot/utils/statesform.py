from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    get_first_name = State()
    get_second_name = State()
    get_number = State()
    get_payment_details = State()
    get_bank_name = State()
    review_data = State()


class MainMenu(StatesGroup):
    main = State()
    packer_menu = State()
    administrator_menu = State()
    manager_menu = State()
