import asyncio

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from aiogram.utils.serialization import deserialize_telegram_object_to_python


class SaveUdpateMiddleware(BaseMiddleware):

    def __init__(self) -> None:
        super().__init__()
        self._storage = None

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict], Awaitable[Any]],
        event: TelegramObject,
        data: dict,
    ) -> Any:
        storage = data.get('psql_storage', None)

        if storage is None:
            if self._storage is None:
                raise ValueError("Database was not configurated. Please, add it to dispatcher data")
        else:
            self._storage = storage

        payload = deserialize_telegram_object_to_python(event)
        user: User = data["event_from_user"]

        await asyncio.gather(
            self._storage.ensure_user_exists(user.id),
            self._storage.save_update(payload),
            return_exceptions=True,
        )

        return await handler(event, data)

