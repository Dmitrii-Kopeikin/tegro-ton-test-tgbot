from typing import List

from aiogram.filters import Filter
from aiogram.types import Message


class JettonFilter(Filter):
    def __init__(self, jettons: List[str]) -> None:
        self.jettons = jettons

    async def __call__(self, message: Message) -> bool:
        '''
        Checks if message.text is a valid jetton.
        '''
        return message.text in self.jettons
