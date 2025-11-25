import time

from bot.dispatcher import Dispatcher
from bot.domain.messenger import Messanger


async def start_long_pooling(dispatcher: Dispatcher, messanger: Messanger) -> None:
    update_offset = 0
    while True:
        updates = await messanger.get_updates(update_offset)

        for update in updates:
            update_offset = max(update_offset, update["update_id"] + 1)
            await dispatcher.dispatch(update)

        time.sleep(1)
