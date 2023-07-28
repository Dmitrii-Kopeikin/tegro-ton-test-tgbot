from fastapi import FastAPI
from pydantic import BaseModel


class IpnResponseData(BaseModel):
    shop_id: str
    amount: str
    order_id: str
    payment_system: int
    currency: str
    test: int
    sign: str

# shop_id	Публичный ключ проекта
# amount	Сумма платежа
# order_id	Идентификатор заказа
# payment_system	Платежная система
# currency	Валюта платежа (RUB, USD, EUR)
# test	Если был задан при оплате
# sign	Подпись запроса