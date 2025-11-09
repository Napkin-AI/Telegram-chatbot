from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.messenger import Messanger
from bot.domain.storage import Storage


class Dispatcher:

    def __init__(self, storage: Storage, messanger: Messanger):
        self._handlers: list[Handler] = []
        self._storage: Storage = storage
        self._messanger: Messanger = messanger

    def add_handlers(self, handlers: list[Handler]) -> None:
        self._handlers.extend(handlers)

    def dispatch(self, update: dict) -> None:

        telegram_id = self._get_telegram_id_from_update(update)
        user = self._storage.get_user(telegram_id)
        user_state = user.get("state") if user else None
        order_json = user["order_json"] if user else "{}"

        if order_json is None:
            order_json = "{}"

        # order_data = json.loads(order_json)

        for handler in self._handlers:
            if handler.can_handle(
                update, user_state, order_json, self._storage, self._messanger
            ):
                if (
                    handler.handle(
                        update, user_state, order_json, self._storage, self._messanger
                    )
                    == HandlerStatus.STOP
                ):
                    break

    def _get_telegram_id_from_update(self, update: dict) -> int | None:
        if "message" in update:
            return update["message"]["from"]["id"]
        elif "callback_query" in update:
            return update["callback_query"]["from"]["id"]
        return None
