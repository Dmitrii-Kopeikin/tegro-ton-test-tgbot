from aiogram.filters import Filter
from aiogram.types import Message


class MnemonicsFilter(Filter):

    async def __call__(self, message: Message) -> bool:
        '''
        Checks if message.text is a valid mnemonics.
        24 words.
        '''
        return len(message.text.split()) == 24
