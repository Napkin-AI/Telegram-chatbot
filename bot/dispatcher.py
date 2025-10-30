import json
import bot.database_client

from bot.handlers.handler import Handler, HandlerStatus


class Dispatcher:

    def __init__(self):
        self._handlers: list[Handler] = []

    def add_handlers(self, handlers: list[Handler]) -> None:
        self._handlers.extend(handlers)

    def dispatch(self, update: dict) -> None:

        telegram_id = self._get_telegram_id_from_update(update)
        user = bot.database_client.get_user(telegram_id)
        user_state = user.get("state") if user else None
        order_json = user['order_json'] if user else '{}'

        if order_json is None:
            order_json = '{}'

        order_data = json.loads(order_json)

        for handler in self._handlers:
            if handler.can_handle(update, user_state, order_json):
                if handler.handle(update, user_state, order_json) == HandlerStatus.STOP:
                    break

    def _get_telegram_id_from_update(self, update: dict) -> int | None:
        if 'message' in update:
            return update['message']['from']['id']
        elif 'callback_query' in update:
            return update['callback_query']['from']['id']
        return None

