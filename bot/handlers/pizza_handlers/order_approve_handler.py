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


class FinishOrder(Handler):

    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messanger: Messanger,
    ) -> bool:
        print(update, state, order_json, sep="\n", end="\n\n\n\n")
        if "callback_query" not in update or state != OrderState.WAIT_FOR_ORDER_APPROVE:
            return False
        return update["callback_query"]["data"].startswith("approve_")

    async def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messanger: Messanger,
    ) -> bool:
        logger.info("[HANDLER] handle FinishOrder start")
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        await asyncio.gather(
            storage.update_user_order(telegram_id, {"approved": callback_data}),
            messanger.answer_callback_query(update["callback_query"]["id"]),
            messanger.delete_message(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                message_id=update["callback_query"]["message"]["message_id"],
            ),
        )

        if callback_data == "approve_restore":
            await messanger.send_message(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text="OK! Please, choose pizza again.",
            )
            update["message"] = {
                "text": "/start",
                "chat": {
                    "id": update["callback_query"]["message"]["chat"]["id"],
                },
                "from": {"id": update["callback_query"]["from"]["id"]},
            }
            logger.info("[HANDLER] handle FinishOrder end")
            return HandlerStatus.CONTINUE
        else:
            await asyncio.gather(
                storage.update_user_state(telegram_id, OrderState.ORDER_FINISHED),
                messanger.send_message(
                    chat_id=update["callback_query"]["message"]["chat"]["id"],
                    text="ORDER SUCCESSFULLY FINISHED!",
                ),
            )
        logger.info("[HANDLER] handle FinishOrder end")
        return HandlerStatus.STOP
