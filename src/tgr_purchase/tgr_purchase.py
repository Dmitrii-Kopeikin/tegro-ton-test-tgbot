import hashlib
import time
import os
import httpx
import urllib.parse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.models import Paylink, Transaction, User


SHOP_ID = os.getenv('SHOP_ID')
SECRET_KEY = os.getenv('SECRET_KEY')
MIN_LIMIT = float(os.getenv('TGR_MIN_LIMIT'))
MAX_LIMIT = float(os.getenv('TGR_MAX_LIMIT'))
CURRENCY = os.getenv('CURRENCY')
URL = os.getenv('PAYMENT_GATEWAY_URL')
FEE_RATE = float(os.getenv('TGR_FEE_RATE'))
TGR_RATE_API_URL = os.getenv('TGR_RATE_API_URL')

PAYMENT_TEST_MODE = os.getenv('PAYMENT_TEST_MODE')


def create_link(amount: int, order_id: int):
    data = {
        'shop_id': SHOP_ID,
        'amount': amount,
        'currency': CURRENCY,
        'order_id': order_id,
    }

    if PAYMENT_TEST_MODE:
        data['test'] = 1

    query_str = urllib.parse.urlencode(sorted(data.items()))
    sign = hashlib.md5(
        (query_str + SECRET_KEY).encode()
    ).hexdigest()
    query_str += f'&sign={sign}'

    return f'{URL}/?{query_str}'


async def buy_TGR_process(amount: float, chat_id: int, session: AsyncSession):
    if amount < MIN_LIMIT:
        return {
            'type': 'error',
            'content': f'Error! Minimum amount for buying TRG: {MIN_LIMIT}. Try again.'
        }

    if amount > MAX_LIMIT:
        return {
            'type': 'error',
            'content': f'Error! Maximum amount for buying TRG: {MAX_LIMIT}. Try again.'
        }

    tgr_rate = await get_tgr_rate()
    if tgr_rate['type'] == 'error':
        return {
            'type': 'error',
            'content': 'Error! Cannot get TGR rate. Try again.'
        }

    fee = amount * FEE_RATE
    total = round((amount + fee) * tgr_rate['content'], 2)

    # Saving paylink to database for checking IPN response
    paylink = Paylink(chat_id=chat_id, created_at=time.time_ns(), is_payed=False, amount=amount)
    session.add(paylink)
    await session.commit()

    link = create_link(total, f'{chat_id}:{paylink.id}')

    return {
        'type': 'success',
        'content': link,
        'cost': total,
        'currency': CURRENCY,
    }


async def get_tgr_rate():
    async with httpx.AsyncClient() as client:
        response = await client.get(TGR_RATE_API_URL)
        if response.status_code == 200:
            return {
                'type': 'success',
                'content': float(response.json()['tegro']['usd']),
            }
        else:
            return {
                'type': 'error',
            }


async def process_ipn_response(data: dict, session: AsyncSession):
    response_sign = data.pop('sign')
    sign = hashlib.md5(
        (urllib.parse.urlencode(data) + SECRET_KEY).encode()
    ).hexdigest()

    chat_id, paylink_id = data['order_id'].split(':')

    if sign != response_sign:
        return {
            'type': 'error',
            'content': 'Error! Invalid sign. Try again.',
            'chat_id': chat_id,
        }

    paylink = await session.get(Paylink, paylink_id)
    if paylink is None:
        return {
            'type': 'error',
            'content': 'Error! Cannot find order. Try again.',
            'chat_id': chat_id,
        }

    if paylink.is_payed:
        q = select(Transaction).where(Transaction.paylink_id == paylink_id)
        transaction = (await session.execute(q)).scalar_one_or_none()
        if transaction:
            return {
                'type': 'error',
                'content': f'Error! Order already payed. Recieved {transaction.amount} TGR.',
                'chat_id': chat_id,
            }

    tgr_rate = await get_tgr_rate()
    if tgr_rate['type'] == 'error':
        return {
            'type': 'error',
            'content': 'Error! Cannot get TGR rate. Try again.',
            'chat_id': chat_id,
        }

    tgr_amount = paylink.amount / tgr_rate['content'] / 100 * (100 - FEE_RATE)

    user = await session.get(User, chat_id)
    if user is None:
        return {
            'type': 'error',
            'content': 'Error! Cannot find user. Try again.',
            'chat_id': chat_id,
        }

    # TODO: Transaction of TGR. Plug for now.
    user.balance += tgr_amount

    paylink.is_payed = True

    transaction = Transaction(
        chat_id=chat_id,
        created_at=time.time_ns(),
        asset='TGR',
        network='TON',
        amount=tgr_amount,
        transaction_type='deposit',
        address='xxx',  # TODO: wallet address.
        paylink_id=paylink.id,
    )
    session.add(transaction)
    await session.commit()

    return {
        'type': 'success',
        'content': f'Payment success! Recieved {tgr_amount} TGR.',
        'tgr_rate': tgr_rate['content'],
        'cost': paylink.amount,
        'fee': paylink.amount / 100 * FEE_RATE,
        'chat_id': chat_id,
    }
