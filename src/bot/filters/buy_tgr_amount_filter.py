from aiogram.filters import Filter
from aiogram.types import Message


class BuyTgrAmountFilter(Filter):
    def __init__(self, max_limit: float, min_limit: float) -> None:
        self.max_limit = max_limit
        self.min_limit = min_limit
    
    async def __call__(self, message: Message) -> bool:
        try:
            amount = float(message.text)
        except ValueError:
            return False
        
        return self.min_limit <= amount <= self.max_limit