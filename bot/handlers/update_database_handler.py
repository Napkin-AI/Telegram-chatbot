from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.messenger import Messanger
from bot.domain.storage import Storage
from bot.domain.order_state import OrderState

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO
)


class UpdateDatabaseHandler(Handler):

    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messanger: Messanger,
    ) -> bool:
        return True

    async def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messanger: Messanger,
    ) -> bool:
        logger.info("[HANDLER] UpdateDatabaseHandler handle start")
        await storage.persist_updates([update])
        logger.info("[HANDLER] UpdateDatabaseHandler handle end")
        return HandlerStatus.CONTINUE
