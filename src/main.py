import time
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from dotenv import load_dotenv

from src.bot.handlers import buy_tgr_router, common_router, ton_interaction_router
from src.bot.middlewares import DbSessionMiddleware
from src.tgr_purchase import process_ipn_response
from src.api.models import IpnResponseData

logging.basicConfig(
    filename='log.txt',
    filemode='a',
    level=logging.INFO,
)

try:
    load_dotenv('.env')
except FileNotFoundError:
    logging.info('No .env file found')


# ==================== Database ====================
engine = create_async_engine('sqlite+aiosqlite:///src/db.sqlite3')
session_maker = async_sessionmaker(engine, expire_on_commit=False)


# ==================== Telegram bot ====================
TOKEN = os.getenv('TOKEN')
URL = os.getenv('URL')

WEBHOOK_PATH = f"/bot/{TOKEN}"
WEBHOOK_URL = URL + WEBHOOK_PATH

bot = Bot(token=TOKEN, parse_mode='HTML')

# For testing. For production using Redis.
if os.getenv('USE_REDIS', 0) == '1' and os.getenv('REDIS_URL'):
    storage = RedisStorage.from_url(os.getenv('REDIS_URL'))
    logging.info('Using Redis storage')
else:
    storage = MemoryStorage()
    logging.info('Using Memory storage')

dp = Dispatcher(storage=storage)
dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))

dp.include_router(common_router)
dp.include_router(buy_tgr_router)
dp.include_router(ton_interaction_router)


# ==================== FastAPI ====================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")


# ==================== HTTP endpoints ====================
@app.post(WEBHOOK_PATH, include_in_schema=False)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot=bot, update=telegram_update)


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    context = {
        'request': request,
        'text': 'Hello world!',
    }
    return templates.TemplateResponse('index.html', context)


@app.post('/payment_response/')
async def payment_response(ipn_response_data: IpnResponseData):
    data = ipn_response_data.model_dump()
    logging.info(f'Payment response: {time.asctime()}. Data: {data}')

    async with session_maker() as session:
        result = await process_ipn_response(data, session)

    chat_id = result['chat_id']
    await bot.send_message(
        chat_id=chat_id,
        text=result['content'],
    )
    return {'status': 'ok'}


# ==================== App events ====================
@app.on_event("startup")
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL
        )
    logging.info('Bot started')
    logging.info('Server started')


@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()
