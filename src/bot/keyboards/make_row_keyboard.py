from typing import List
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def make_row_keyboard(items: List[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)
