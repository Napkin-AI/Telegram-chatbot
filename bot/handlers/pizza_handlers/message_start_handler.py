import json

from bot.handlers.pizza_handlers import json_data
from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.messenger import Messanger
from bot.domain.storage import Storage
from bot.domain.order_state import OrderState


class MessageStartHandler(Handler):

    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messanger: Messanger,
    ) -> bool:
        print(update)
        return (
            "message" in update
            and "text" in update["message"]
            and update["message"]["text"] == "/start"
        )

    def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messanger: Messanger,
    ) -> bool:
        telegram_id = update["message"]["from"]["id"]
        storage.clear_user_state_order(telegram_id)
        storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_NAME)

        messanger.send_message(
            chat_id=update["message"]["chat"]["id"],
            text="Hello to telegram Pizza shop bot!",
            reply_markup=json.dumps({"remove_keyboard": True}),
        )

        messanger.send_message(
            chat_id=update["message"]["chat"]["id"],
            text="Choose pizza",
            reply_markup=json_data.select_pizza,
        )

        return HandlerStatus.STOP
