from typing import Any, List
from aiogram.filters import Filter


class JettonFilter(Filter):
    def __init__(self, jettons: List[str]) -> None:
        self.jettons = jettons

    async def __call__(self, jetton: str) -> bool:
        return jetton in self.jettons
