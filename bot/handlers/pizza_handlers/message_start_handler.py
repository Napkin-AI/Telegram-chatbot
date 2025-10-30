import json

import bot.telegram_client
import bot.database_client
from bot.handlers.pizza_handlers import json_data
from bot.handlers.handler import Handler, HandlerStatus


class MessageStartHandler(Handler):

    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        return 'message' in update and 'text' in update['message'] and \
               update['message']['text'] == '/start'

    def handle(self, update: dict, state: str, order_json: dict) -> bool:
        telegram_id = update['message']['from']['id']
        bot.database_client.clear_user_state_order(telegram_id)
        bot.database_client.update_user_state(telegram_id, "WAIT_FOR_PIZZA_NAME")

        bot.telegram_client.send_message(
            chat_id=update['message']['chat']['id'],
            text="Hello to telegram Pizza shop bot!",
            reply_markup=json.dumps({'remove_keyboard': True})
        )

        bot.telegram_client.send_message(
            chat_id=update['message']['chat']['id'],
            text="Choose pizza",
            reply_markup=json_data.select_pizza
        )

        return HandlerStatus.STOP
