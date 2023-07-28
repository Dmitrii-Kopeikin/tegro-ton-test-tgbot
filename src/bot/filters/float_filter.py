from aiogram.filters import Filter
from aiogram.types import Message


class FloatFilter(Filter):

    async def __call__(self, message: Message) -> bool:
        '''
        Checks if message.text is a valid float.
        '''
        try:
            float(message.text)
            return True
        except ValueError:
            return False
