import bot.telegram_client
import bot.database_client
from bot.handler import Handler

class DatabaseHandler(Handler):

    def can_handle(self, update: dict) -> bool:
        return True

    def handle(self, update: dict) -> bool:
        bot.database_client.persist_updates([update])
        return True
