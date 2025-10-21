import time

import bot
from bot.dispatcher import Dispatcher


def start_long_pooling(dispatcher: Dispatcher) -> None:
    update_offset = 0
    while True:
            updates = bot.telegram_client.getUpdates(update_offset)

            for update in updates:
                update_offset = max(update_offset, update['update_id'] + 1)
                dispatcher.dispatch(update)

            time.sleep(1)
