from abc import ABC, abstractmethod
from bot.domain.order_state import OrderState


class Storage(ABC):
    @abstractmethod
    def recreate_database(self) -> None:
        pass

    @abstractmethod
    def ensure_user_exists(self, telegram_id: int) -> None:
        pass

    @abstractmethod
    def clear_user_state_order(self, telegram_id: int) -> None:
        pass

    @abstractmethod
    def update_user_state(self, telegram_id: int, state: OrderState) -> None:
        pass

    @abstractmethod
    def persist_updates(self, updates: list) -> None:
        pass

    @abstractmethod
    def get_user(self, telegram_id: int | None) -> dict | None:
        pass

    @abstractmethod
    def update_user_order(self, telegram_id: int, order: dict) -> None:
        pass

    @abstractmethod
    def get_user_order(self, telegram_id: int | None) -> dict | None:
        pass
