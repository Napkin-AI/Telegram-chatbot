from bot.handlers.pizza_handlers import json_data
from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.messenger import Messanger
from bot.domain.storage import Storage
from bot.domain.order_state import OrderState


class SelectDrinks(Handler):

    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messanger: Messanger,
    ) -> bool:
        if "callback_query" not in update or state != OrderState.WAIT_FOR_DRINKS:
            return False
        return update["callback_query"]["data"].startswith("drink_")

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
        drink = callback_data.replace("drink_", "").title()

        storage.update_user_order(telegram_id, {"drink": drink})
        storage.update_user_state(telegram_id, OrderState.WAIT_FOR_ORDER_APPROVE)

        messanger.answer_callback_query(update["callback_query"]["id"])
        messanger.delete_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        user_order = storage.get_user_order(telegram_id)

        if not user_order:
            messanger.send_message(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text="The backet is empty! Something gone wrong!",
            )
            storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_NAME)
            return HandlerStatus.CONTINUE
        else:
            print(f"\033[92mUSER_ORDER:\033[0m {type(user_order)}", user_order)
            messanger.send_message(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text=f"Approve order\nPizza: {user_order['pizza_name']}\nSize: {user_order['pizza_size']}\nDrink: {user_order['drink']}",
                reply_markup=json_data.approve_json,
            )

        return HandlerStatus.STOP
