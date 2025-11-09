from bot.handlers import get_handlers
from bot.long_pooling import start_long_pooling
from bot.dispatcher import Dispatcher
from bot.domain.messenger import Messanger
from bot.domain.storage import Storage
from bot.infrastructure.database_sqlite import StorageSqlite
from bot.infrastructure.messanger_telegram import MessangerTelegram


def main() -> None:
    print("\n\033[42mBot is active!\033[0m\n")
    try:
        storage: Storage = StorageSqlite()
        messanger: Messanger = MessangerTelegram()

        dispatcher = Dispatcher(storage, messanger)
        dispatcher.add_handlers(get_handlers())
        start_long_pooling(dispatcher, messanger)
    except KeyboardInterrupt:
        print("\n\033[41mBot is inactive!\033[0m\n")


if __name__ == "__main__":
    main()
