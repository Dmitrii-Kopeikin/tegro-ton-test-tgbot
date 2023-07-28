from enum import Enum
from aiogram import types, Router, F
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.bot.keyboards import (
    make_main_menu_keyboard,
    make_ton_menu_keyboard,
    make_cancel_keyboard,
)

from src.ton_tools import get_ton_client, get_available_jettons
from src.bot.handlers.common import AppState
from src.bot.filters import (
    MnemonicsFilter,
    WalletAddressFilter,
    FloatFilter,
    JettonFilter,
)


class TonInteractionStates(StatesGroup):
    ton_choose_action = State()

    enter_address_get_balance = State()
    enter_address_get_transaction = State()
    enter_address_send_transaction = State()

    enter_mnemonics = State()
    enter_amount = State()

    enter_jetton = State()


class Action(Enum):
    SEND_TRANSACTION = 1
    SEND_TRANSACTION_JETTON = 2
    GET_BALANCE = 3
    GET_TRANSACTION = 4


AVAILABLE_JETTONS = get_available_jettons()

router = Router()


@router.message(F.text.lower() == 'ton operations', AppState.idle)
async def ton_operations(message: types.Message, state: FSMContext):

    await state.set_state(TonInteractionStates.ton_choose_action)

    await message.answer(
        text=f'Choose action',
        reply_markup=make_ton_menu_keyboard(),
    )


@router.message(F.text.casefold() == 'create wallet', TonInteractionStates.ton_choose_action)
async def create_wallet(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(AppState.idle)

    ton_client = get_ton_client()
    response = await ton_client.create_wallet()

    if response['status'] == 'success':
        response_data = response['result']
        ton_address = response_data['address']
        # mnemonics = response_data['mnemonic']
        mnemonics_string = response_data['mnemonicStr']
        public_key = response_data['publicKey']
        private_key = response_data['privateKey']

        jettons = response_data['jettons']

        wallets_list = [f'TON: {ton_address}'] + [f'{jetton}: {address}' for jetton, address in jettons.items()]
        wallets_text = '  \n'.join(wallets_list)

        text = f'Your wallets:\n  {wallets_text}\n'
        text += f'Your mnemonics:  {mnemonics_string}\n'
        text += f'Your public key: {public_key}\n'
        text += f'Your private key: {private_key}\n'

        await message.answer(
            text=text,
            reply_markup=make_main_menu_keyboard(),
        )
        return

    await message.answer(
        text=f'Error: {response["error"]}',
        reply_markup=make_main_menu_keyboard(),
    )


@router.message(F.text.casefold() == 'get balance', TonInteractionStates.ton_choose_action)
async def get_balance(message: types.Message, state: FSMContext):
    await state.set_state(TonInteractionStates.enter_address_get_balance)

    await message.answer(
        text=f'Enter wallet address',
        reply_markup=make_cancel_keyboard(),
    )


@router.message(WalletAddressFilter(), TonInteractionStates.enter_address_get_balance)
async def enter_address_get_balance(message: types.Message, state: FSMContext):
    address = message.text
    ton_client = get_ton_client()
    response = await ton_client.get_balance(address)
    if response['status'] == 'success':
        await state.clear()
        await state.set_state(AppState.idle)
        balance = response['result']['balance']
        await message.answer(
            text=f'Wallet: {address}\nBalance: {balance}',
            reply_markup=make_main_menu_keyboard(),
        )
        return

    await message.answer(
        text=f'Error: {response["error"]}. Please, try again',
    )


@router.message(F.text.casefold() == 'get transaction', TonInteractionStates.ton_choose_action)
async def get_transaction(message: types.Message, state: FSMContext):
    await state.set_state(TonInteractionStates.enter_address_get_transaction)

    await message.answer(
        text=f'Enter transaction address',
        reply_markup=make_cancel_keyboard(),
    )


@router.message(WalletAddressFilter(), TonInteractionStates.enter_address_get_transaction)
async def enter_address_get_transaction(message: types.Message, state: FSMContext):
    address = message.text
    ton_client = get_ton_client()
    response = await ton_client.get_transaction(address)
    if response['status'] == 'success':
        await state.clear()
        await state.set_state(AppState.idle)
        await message.answer(
            text=f'Result: {response["result"]}',
            reply_markup=make_main_menu_keyboard(),
        )
        return

    await message.answer(
        text=f'Error: {response["error"]}. Please, try again',
    )


@router.message(
    or_f(
        F.text.casefold() == 'send ton transaction',
        F.text.casefold() == 'send jetton transaction',
    ),
    TonInteractionStates.ton_choose_action,
)
async def send_transaction(message: types.Message, state: FSMContext):
    if message.text.casefold() == 'send ton transaction':
        action = Action.SEND_TRANSACTION
    else:
        action = Action.SEND_TRANSACTION_JETTON

    await state.update_data(action=action)

    await state.set_state(TonInteractionStates.enter_address_send_transaction)

    await message.answer(
        text=f'Enter destination wallet address',
        reply_markup=make_cancel_keyboard(),
    )


@router.message(WalletAddressFilter(), TonInteractionStates.enter_address_send_transaction)
async def enter_address_send_transaction(message: types.Message, state: FSMContext):
    address = message.text
    await state.update_data(address=address)
    await state.set_state(TonInteractionStates.enter_amount)

    await message.answer(
        text=f'Enter amount',
        reply_markup=make_cancel_keyboard(),
    )


@router.message(FloatFilter(), TonInteractionStates.enter_amount)
async def enter_amount(message: types.Message, state: FSMContext):
    amount = float(message.text)
    await state.update_data(amount=amount)

    await state.set_state(TonInteractionStates.enter_mnemonics)
    await message.answer(
        text=f'Enter mnemonics',
        reply_markup=make_cancel_keyboard(),
    )


@router.message(MnemonicsFilter(), TonInteractionStates.enter_mnemonics)
async def enter_mnemonics(message: types.Message, state: FSMContext):
    mnemonics = message.text
    await state.update_data(mnemonics=mnemonics)

    if (await state.get_data())['action'] == Action.SEND_TRANSACTION_JETTON:
        await state.set_state(TonInteractionStates.enter_jetton)

        await message.answer(
            text=f'Enter jetton.(Available jettons: {", ".join(AVAILABLE_JETTONS)})',
            reply_markup=make_cancel_keyboard(),
        )
        return

    data = await state.get_data()

    await state.clear()
    await state.set_state(AppState.idle)

    result = await process_send_transaction(data)

    await message.answer(
        text=f'Result of request: {result}',
        reply_markup=make_main_menu_keyboard(),
    )


@router.message(JettonFilter(AVAILABLE_JETTONS), TonInteractionStates.enter_jetton)
async def enter_jetton(message: types.Message, state: FSMContext):
    jetton = message.text
    await state.update_data(jetton=jetton)

    data = await state.get_data()

    await state.clear()
    await state.set_state(AppState.idle)

    result = await process_send_transaction_jetton(data)

    await message.answer(
        text=f'Result of request: {result}',
        reply_markup=make_main_menu_keyboard(),
    )


@router.message(TonInteractionStates.enter_jetton)
async def enter_jetton_incorrect(message: types.Message, state: FSMContext):
    await message.answer(
        text=f'Error: invalid jetton. Please, check the jetton and try again.',
    )


@router.message(TonInteractionStates.enter_mnemonics)
async def enter_mnemonics_incorrect(message: types.Message, state: FSMContext):
    await message.answer(
        text=f'Error: invalid mnemonics. Please, check the mnemonics and try again.',
    )


@router.message(TonInteractionStates.enter_amount)
async def enter_amount_incorrect(message: types.Message, state: FSMContext):
    await message.answer(
        text=f'Error: invalid amount. Please, check the amount and try again.',
    )


@router.message(
    or_f(
        TonInteractionStates.enter_address_get_balance,
        TonInteractionStates.enter_address_get_transaction,
        TonInteractionStates.enter_address_send_transaction,
    ),
)
async def enter_address_incorrect(message: types.Message, state: FSMContext):
    await message.answer(
        text=f'Error: invalid address. Please, check the address and try again.',
    )


async def process_send_transaction(data: dict):
    address = data['address']
    amount = data['amount']
    mnemonics = data['mnemonics']

    ton_client = get_ton_client()

    response = await ton_client.send_transaction(address, amount, mnemonics)

    if response['status'] == 'success':
        return response['result']
    return response['error']


async def process_send_transaction_jetton(data: dict):
    address = data['address']
    amount = data['amount']
    mnemonics = data['mnemonics']
    jetton = data['jetton']

    ton_client = get_ton_client()

    response = await ton_client.send_transaction_jetton(address, amount, mnemonics, jetton)

    if response['status'] == 'success':
        return response['result']
    return response['error']
