from bot.handlers.pizza_handlers import json_data
from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.messenger import Messanger
from bot.domain.storage import Storage


class SelectPizzaSize(Handler):

    def can_handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messanger: Messanger,
    ) -> bool:
        if "callback_query" not in update or state != "WAIT_FOR_PIZZA_SIZE":
            return False
        return update["callback_query"]["data"].startswith("size_")

    def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messanger: Messanger,
    ) -> bool:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]
        pizza_size = callback_data.replace("size_", "").title()

        storage.update_user_order(telegram_id, {"pizza_size": pizza_size})
        storage.update_user_state(telegram_id, "WAIT_FOR_DRINKS")

        messanger.answer_callback_query(update["callback_query"]["id"])
        messanger.delete_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        messanger.send_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text="Choose drink",
            reply_markup=json_data.select_drinks,
        )

        return HandlerStatus.STOP
