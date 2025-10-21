from bot.handler import Handler

class Dispatcher:

    def __init__(self):
        self._handlers: list[Handler] = []

    def add_handlers(self, handlers: list[Handler]) -> None:
        self._handlers.extend(handlers)

    def dispatch(self, update: dict) -> None:
        for handler in self._handlers:
            if handler.can_handle(update):
                if not handler.handle(update):
                    break
