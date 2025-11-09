from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.messenger import Messanger
from bot.domain.storage import Storage


class UpdateDatabaseHandler(Handler):

    def can_handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messanger: Messanger,
    ) -> bool:
        return True

    def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messanger: Messanger,
    ) -> bool:
        storage.persist_updates([update])
        return HandlerStatus.CONTINUE
