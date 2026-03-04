from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    async def ensure_user_exists(self, telegram_id: int) -> None: ...

    @abstractmethod
    async def save_update(self, update: dict) -> None: ...

    @abstractmethod
    async def recreate_database(self) -> None: ...

    @abstractmethod
    async def get_history(self, telegram_id: int) -> list[str]: ...

    @abstractmethod
    async def clean_history(self, telegram_id: int) -> None: ...

    @abstractmethod
    async def get_stats(self, telegram_id: int) -> list[tuple[str, int]]: ...

    @abstractmethod
    async def save_user_query(self, telegram_id: int, query: str) -> None: ...
