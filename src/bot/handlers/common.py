import logging
import time

from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.keyboards import make_main_menu_keyboard

from src.db.models import User


class AppState(StatesGroup):
    idle = State()


router = Router()


@router.message(Command(commands=['start']))
async def start_handler(message: types.Message, state: FSMContext, session: AsyncSession):
    chat_id = message.chat.id

    user_object = await session.get(User, chat_id)
    if user_object is None:
        session.add(User(chat_id=chat_id))
        await session.commit()

    await state.set_state(AppState.idle)

    await message.reply(
        text=f"Hello! Choose action!",
        reply_markup=make_main_menu_keyboard(),
    )


@router.message(Command(commands=['cancel']))
@router.message(F.text.lower() == 'cancel')
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(AppState.idle)
    await message.reply(
        text=f"Canceled.",
        reply_markup=make_main_menu_keyboard(),
    )


@router.message(Command(commands=['get_state']))
# For debug
async def get_state_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    await message.reply(
        text=f"Current state: {current_state}"
    )
