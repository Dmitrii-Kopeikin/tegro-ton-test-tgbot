# Tegro Ton Bot

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.0.0b8-blue)](https://docs.aiogram.dev/en/latest/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0-blue)](https://fastapi.tiangolo.com/)
[![Redis](https://img.shields.io/badge/Redis-4.6.0-blue)](https://redis.io/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-1.4.23-blue)](https://www.sqlalchemy.org/)
[![httpx](https://img.shields.io/badge/httpx-0.24.1-blue)](https://www.python-httpx.org/)

## Описание

Tegro Ton Bot - это Telegram-бот, который предназначен для работы с платежной системой Tegro.money и блокчейном TON.

Бот позволяет пользователям отправлять и получать платежи, проверять баланс и информацию о транзакциях, а также выполнять другие операции, связанные с блокчейном TON и джеттоном TGR.

Данный бот разрабатывался как тестовое задание. Покупка TGR в нем реализована исключительно для теста платежной системы.

## Функции

- Покупка TGR
- Проверка баланса TGR
- Создание кошелька TON
- Создание кошелька TGR
- Проверка транзакций в сети TON
- Создание транзакций TON
- Создание транзакций TGR
- Проверка баланса кошелька TON
- Проверка баланса кошелька TGR

## Использованные технологии

- Python 3.11
- [Aiogram](https://docs.aiogram.dev/en/latest/) - Python-фреймворк для создания Telegram-ботов
- [FastAPI](https://fastapi.tiangolo.com/) - Python-фреймворк для создания веб-приложений с высокой производительностью
- [Uvicorn](https://www.uvicorn.org/) - ASGI-сервер, используемый для запуска FastAPI
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python-библиотека для работы с реляционными базами данных
- [Alembic](https://alembic.sqlalchemy.org/en/latest/) - Python-библиотека для миграции баз данных
- [httpx](https://www.python-httpx.org/) - Python-библиотека для выполнения HTTP-запросов
- [Redis](https://redis.io/) - In-memory база данных с открытым исходным кодом



## Установка

В первую очередь необходимо зарегистрировать бота в сети Telegram и получить токен. Для этого можно воспользоваться ботом @BotFather.

Данный бот использует Telegram Hook. Следовательно для его запуска нужен белый IP, или можно использовать утилиту и сервис https://ngrok.com.

Перед запуском необходимо переименовать файл '.env.template' в '.env' и заполнить в нем все переменные.

Для работы с сетью TON необходимо скачать Ton-Server из репозитория https://github.com/TGRTON/TON-token-Rest-API и
запустить его согласно инструкции.

Для приема платежей необходимо зарегистрировать магазин в сервисе https://tegro.money.

Для запуска из корневой директории выполнить:
```
uvicorn src.main:app --port=80
```

## Использование

После ввода команды /start появляется интуитивно понятное меню. С его помощью можно протестировать весь функционал бота.