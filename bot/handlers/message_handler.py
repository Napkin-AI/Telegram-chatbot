import bot.telegram_client
from bot.handlers.handler import Handler, HandlerStatus


class MessageHandler(Handler):

    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        return 'message' in update and 'text' in update['message']

    def handle(self, update: dict, state: str, order_json: dict) -> bool:
        bot.telegram_client.send_message(
            chat_id=update['message']['chat']['id'],
            text=update['message']['text']
        )
        return HandlerStatus.STOP
