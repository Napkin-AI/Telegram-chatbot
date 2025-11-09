from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.messenger import Messanger
from bot.domain.storage import Storage


class EnsureUserExists(Handler):

    def can_handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messanger: Messanger,
    ) -> bool:
        return "message" in update and "from" in update["message"]

    def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messanger: Messanger,
    ) -> bool:
        telegram_id = update["message"]["from"]["id"]
        storage.ensure_user_exists(telegram_id)
        return HandlerStatus.CONTINUE
