from abc import ABC, abstractmethod
from enum import Enum
from bot.domain.messenger import Messanger
from bot.domain.storage import Storage


class HandlerStatus(Enum):
    CONTINUE = 1
    STOP = 2


class Handler(ABC):

    @abstractmethod
    def can_handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messanger: Messanger,
    ) -> bool:
        pass

    @abstractmethod
    def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messanger: Messanger,
    ) -> HandlerStatus:
        pass
