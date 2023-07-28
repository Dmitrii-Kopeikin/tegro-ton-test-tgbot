from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User
from src.bot.keyboards import (
    make_tgr_menu_keyboard,
    make_cancel_keyboard,
    make_approve_keyboard,
    make_main_menu_keyboard,
)
from src.buy_tgr_tools import buy_TGR_process
from src.bot.handlers.common import AppState


router = Router()


class TgrInteractionState(StatesGroup):
    choose_action = State()

    typing_amount = State()
    approve = State()


@router.message(F.text.casefold() == 'tgr operations', AppState.idle)
async def tgr_operations(message: types.Message, state: FSMContext):
    await state.set_state(TgrInteractionState.choose_action)
    await message.answer(
        text=f'What do you want to do?',
        reply_markup=make_tgr_menu_keyboard(),
    )


# @router.message(TgrInteractionState.choose_action)
@router.message(F.text.casefold() == 'buy tgr', TgrInteractionState.choose_action)
async def buy_tgr(message: types.Message, state: FSMContext):
    await state.set_state(TgrInteractionState.typing_amount)
    await message.answer(
        text=f'How much TGR do you want to buy?',
        reply_markup=make_cancel_keyboard(),
    )


@router.message(TgrInteractionState.typing_amount)
async def amount_tgr(message: types.Message, state: FSMContext):
    amount = 0
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer(text=f'Incorrect amount. Please, try again.')
        return

    await state.update_data(amount=amount)
    await state.set_state(TgrInteractionState.approve)
    await message.answer(
        text=f'You want to buy {amount} TGR. Is that correct?',
        reply_markup=make_approve_keyboard(),
    )


@router.message(F.text.casefold() == 'yes', TgrInteractionState.approve)
async def approve_yes(message: types.Message, state: FSMContext, session: AsyncSession):
    amount = (await state.get_data())["amount"]

    result = await buy_TGR_process(amount, message.from_user.id, session)
    if result['type'] == 'error':
        await message.answer(
            text=result['content'],
            reply_markup=make_main_menu_keyboard(),
        )
        return

    await state.clear()
    await state.set_state(AppState.idle)
    await message.answer(
        text=f'To buy {amount} TGR, for {result["cost"]}{result["currency"]} follow link:\n {result["content"]}',
        reply_markup=make_main_menu_keyboard(),
    )


@router.message(F.text.casefold() == 'no', TgrInteractionState.approve)
async def approve_no(message: types.Message, state: FSMContext):
    await state.set_state(TgrInteractionState.typing_amount)
    await message.answer(
        text=f'How much TGR do you want to buy?',
        reply_markup=make_cancel_keyboard(),
    )


@router.message(TgrInteractionState.approve)
async def approve_incorrect(message: types.Message):
    await message.answer(text='Please answer "Yes" or "No".')


@router.message(F.text.casefold() == 'get balance', TgrInteractionState.choose_action)
async def get_balance_handler(message: types.Message, session: AsyncSession):
    chat_id = message.chat.id
    user_object = await session.get(User, chat_id)
    if user_object is None:
        session.add(User(chat_id=chat_id))
        await session.commit()

    await message.reply(
        text=f"Your balance: {user_object.balance} TGR",
    )


# TODO: Implement command to manually check order is payed.
# @router.message(Command(commands=['check_order']))
# async def check_order(message: types.Message, session: AsyncSession):
#     ...
