import time
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.bot.handlers import buy_tgr_router, common_router, ton_interaction_router
from src.bot.middlewares import DbSessionMiddleware

from src.buy_tgr_tools import process_ipn_response

logging.basicConfig(filemode='a', level=logging.INFO)


# ==================== Database ====================
engine = create_async_engine('sqlite+aiosqlite:///src/db.sqlite3')
session_maker = async_sessionmaker(engine, expire_on_commit=False)

# ==================== Telegram bot ====================
TOKEN = os.getenv('TOKEN')
URL = os.getenv('URL')

WEBHOOK_PATH = f"/bot/{TOKEN}"
WEBHOOK_URL = URL + WEBHOOK_PATH

bot = Bot(token=TOKEN, parse_mode='HTML')
# For testing. For production use Redis or implement CustomStorage
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))

dp.include_router(common_router)
dp.include_router(buy_tgr_router)
dp.include_router(ton_interaction_router)

# ==================== FastAPI ====================
app = FastAPI()
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

# ==================== HTTP endpoints ====================


@app.post(WEBHOOK_PATH)
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


@app.post('/payment_response')
async def payment_response(request: Request):
    logging.info(f'Payment response: {time.asctime()}. Request: {request}')
    data = await request.json()
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


@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()
