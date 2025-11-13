from bot.handlers.pizza_handlers import json_data
from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.messenger import Messanger
from bot.domain.storage import Storage
from bot.domain.order_state import OrderState


class SelectPizzaHandler(Handler):

    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messanger: Messanger,
    ) -> bool:
        if "callback_query" not in update or state != OrderState.WAIT_FOR_PIZZA_NAME:
            return False
        return update["callback_query"]["data"].startswith("pizza_")

    def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messanger: Messanger,
    ) -> bool:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]
        pizza_name = callback_data.replace("pizza_", "").replace("_", "").title()
        storage.update_user_order(telegram_id, {"pizza_name": pizza_name})
        storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_SIZE)

        messanger.answer_callback_query(update["callback_query"]["id"])
        messanger.delete_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        messanger.send_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text="Choose pizza size",
            reply_markup=json_data.select_size,
        )

        return HandlerStatus.STOP
