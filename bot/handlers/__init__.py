from bot.handlers.handler import Handler
from bot.handlers.update_database_handler import UpdateDatabaseHandler
from bot.handlers.message_handler import MessageHandler
from bot.handlers.photo_handler import PhotoHandler
from bot.handlers.sticker_handler import StickerHandler
from bot.handlers.ensure_user_exist_handler import EnsureUserExists
from bot.handlers.pizza_handlers.message_start_handler import MessageStartHandler

def get_handlers() -> list[Handler]:
    return [
        UpdateDatabaseHandler(),
        EnsureUserExists(),
        MessageStartHandler(),
        MessageHandler(),
        PhotoHandler(),
        StickerHandler()
    ]
