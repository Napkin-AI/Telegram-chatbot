import bot.telegram_client
from bot.handlers.handler import Handler, HandlerStatus

class StickerHandler(Handler):

    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        return 'message' in update and 'sticker' in update['message']

    def handle(self, update: dict, state: str, order_json: dict) -> bool:
        bot.telegram_client.send_sticker(
            chat_id=update['message']['chat']['id'],
            sticker=update['message']['sticker']['file_id']
        )
        return HandlerStatus.STOP
