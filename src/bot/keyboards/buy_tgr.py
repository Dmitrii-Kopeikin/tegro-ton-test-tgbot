from aiogram.types import ReplyKeyboardMarkup

from .make_row_keyboard import make_row_keyboard

def make_tgr_menu_keyboard() -> ReplyKeyboardMarkup:
    return make_row_keyboard(['Buy TGR', 'Get balance', 'Cancel'])