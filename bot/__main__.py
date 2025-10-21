import time

import bot.database_client
import bot.telegram_client

from bot.handlers import (
    message_handler,
    sticker_handler,
    database_handler,
    photo_handler
)
from bot.long_pooling import start_long_pooling
from bot.dispatcher import Dispatcher

def main() -> None:
    offset: int = 0
    print("\n\033[42mBot is active!\033[0m\n")
    handlers = [
        database_handler.DatabaseHandler(),
        message_handler.MessageHandler(),
        sticker_handler.StickerHandler(),
        photo_handler.PhotoHandler()
        ]

    try:
        dispatcher = Dispatcher()
        dispatcher.add_handlers(handlers)
        start_long_pooling(dispatcher)
    except KeyboardInterrupt:
        print("\n\033[41mBot is inactive!\033[0m\n")


if __name__ == '__main__':
    main()