import re

from aiogram.filters import Filter
from aiogram.types import Message


class WalletAddressFilter(Filter):

    async def __call__(self, message: Message) -> bool:
        '''
        Checks if message.text is a valid wallet address.
        base64 or base64url.
        Length: 48 symbols.
        '''
        return re.match(r'^[A-Za-z0-9+/]{48}$|^[A-Za-z0-9_-]{48}$', message.text)
