import bot.telegram_client
from bot.handlers.handler import Handler, HandlerStatus

class PhotoHandler(Handler):

    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        return 'message' in update and 'photo' in update['message']

    def handle(self, update: dict, state: str, order_json: dict) -> bool:
        best_photo = max(update['message']['photo'], key=lambda p: p['width'] * p['height'])

        bot.telegram_client.send_photo(
            chat_id=update['message']['chat']['id'],
            photo=best_photo['file_id']
        )
        return HandlerStatus.STOP

