from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.domain.storage import Storage


class PSQLInjection(BaseMiddleware):

    def __init__(self, storage: Storage) -> None:
        super().__init__()
        self._storage = storage

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict], Awaitable[Any]],
        event: TelegramObject,
        data: dict,
    ) -> Any:

        data["psql_storage"] = self._storage
        print("was here")
        return await handler(event, data)
