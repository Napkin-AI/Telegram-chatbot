from bot.handlers import get_handlers
from bot.long_pooling import start_long_pooling
from bot.dispatcher import Dispatcher

def main() -> None:
    offset: int = 0
    print("\n\033[42mBot is active!\033[0m\n")
    try:
        dispatcher = Dispatcher()
        dispatcher.add_handlers(get_handlers())
        start_long_pooling(dispatcher)
    except KeyboardInterrupt:
        print("\n\033[41mBot is inactive!\033[0m\n")


if __name__ == '__main__':
    main()