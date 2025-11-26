from bot.handlers.pizza_handlers import json_data
from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.messenger import Messanger
from bot.domain.storage import Storage
from bot.domain.order_state import OrderState
import asyncio

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO
)


class SelectPizzaSize(Handler):

    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messanger: Messanger,
    ) -> bool:
        if "callback_query" not in update or state != OrderState.WAIT_FOR_PIZZA_SIZE:
            return False
        return update["callback_query"]["data"].startswith("size_")

    async def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messanger: Messanger,
    ) -> bool:
        logger.info("[HANDLER] SelectPizzaSize handle start")
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]
        pizza_size = callback_data.replace("size_", "").title()

        await asyncio.gather(
            storage.update_user_order(telegram_id, {"pizza_size": pizza_size}),
            storage.update_user_state(telegram_id, OrderState.WAIT_FOR_DRINKS),
            messanger.answer_callback_query(update["callback_query"]["id"]),
            messanger.delete_message(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                message_id=update["callback_query"]["message"]["message_id"],
            ),
            messanger.send_message(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text="Choose drink",
                reply_markup=json_data.select_drinks,
            ),
        )
        logger.info("[HANDLER] SelectPizzaSize handle end")
        return HandlerStatus.STOP
