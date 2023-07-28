from fastapi import Form
from pydantic import BaseModel

from .decorators import form_body


@form_body
class IpnResponseData(BaseModel):
    id: str
    shop_id: str
    date_created: str
    date_payed: str
    status: str
    payment_system: str
    currency_id: str
    currency: str
    amount: float
    fee: str
    order_id: str
    public_key: str
    test: int | None = None
    sign: str

    # "id": "87ec221bdbc2a85567946c9adde1e2f8",
    # "shop_id": "EC0D29273292A9A5EEFA9B95BE42687E",
    # "date_created": "2023-07-29 00:47:07",
    # "date_payed": "2023-07-29 00:47:08",
    # "status": "1",
    # "payment_system": "45",
    # "currency_id": "2",
    # "currency": "USD",
    # "amount": 21877.52,
    # "fee": "459.43",
    # "order_id": "1686381545:2",
    # "public_key": "EC0D29273292A9A5EEFA9B95BE42687E",
    # "test": 1,
    # "sign": "dbfa7f3a709ab11d1bd758eed1ca4864"