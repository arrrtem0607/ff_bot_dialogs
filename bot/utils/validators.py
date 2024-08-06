import re


def validate_name(name: str) -> str:
    if not re.match(r'^[а-яА-ЯёЁ]+$', name):
        raise ValueError("Имя должно содержать только буквы кириллицы")
    return name.capitalize()


def validate_phone_number(phone: str) -> str:
    patterns = [
        r'^\+7\d{10}$',
        r'^7\d{10}$',
        r'^8\d{10}$',
        r'^\d{10}$'
    ]
    if not any(re.match(pattern, phone) for pattern in patterns):
        raise ValueError("Номер телефона должен соответствовать одному из шаблонов\n"
                         "+7...(10 цифр)\n"
                         "7...(10 цифр)\n"
                         "8...(10 цифр)\n"
                         "10 цифр\n")

    phone = re.sub(r'^[78]', '+7', phone) if phone.startswith(('7', '8')) else f'+7{phone}'
    return phone


def validate_payment_details(details: str) -> str:
    return validate_phone_number(details)  # Используем ту же валидацию, что и для номера телефона


def validate_bank_name(bank: str) -> str:
    if not re.match(r'^[а-яА-ЯёЁ\s]+$', bank):
        raise ValueError("Название банка должно содержать только буквы кириллицы и пробелы")
    return bank.capitalize()
