import bot.telegram_client
from bot.handler import Handler

class PhotoHandler(Handler):

    def can_handle(self, update: dict) -> bool:
        return 'message' in update and 'photo' in update['message']

    def handle(self, update: dict) -> bool:
        best_photo = max(update['message']['photo'], key=lambda p: p['width'] * p['height'])

        bot.telegram_client.sendPhoto(
            chat_id=update['message']['chat']['id'],
            photo=best_photo['file_id']
        )
        return False
