from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def make_multirow_keyboard(items: list[list[str]]) -> ReplyKeyboardMarkup:
    keyboard = []
    for row in items:
        keyboard.append([KeyboardButton(text=item) for item in row])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)