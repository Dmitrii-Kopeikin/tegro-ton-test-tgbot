from aiogram.types import ReplyKeyboardMarkup

from .make_multirow_keyboard import make_multirow_keyboard


def make_ton_menu_keyboard() -> ReplyKeyboardMarkup:
    return make_multirow_keyboard([
        [
            'Create wallet',
            'Get balance',
            'Get transaction',
        ],
        [
            'Send TON transaction',
            'Send Jetton transaction',
            'Cancel',
        ],
    ])
