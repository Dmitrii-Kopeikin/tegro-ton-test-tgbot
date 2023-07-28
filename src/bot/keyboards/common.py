from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from .make_row_keyboard import make_row_keyboard

def make_main_menu_keyboard() -> ReplyKeyboardMarkup:
    return make_row_keyboard(['TGR operations', 'TON operations'])

def make_cancel_keyboard() -> ReplyKeyboardMarkup:
    return make_row_keyboard(['Cancel'])

def make_approve_keyboard() -> ReplyKeyboardMarkup:
    return make_row_keyboard(['Yes', 'No', 'Cancel'])