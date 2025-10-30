import bot.telegram_client
import bot.database_client
from bot.handlers.pizza_handlers import json_data
from bot.handlers.handler import Handler, HandlerStatus


class SelectPizzaSize(Handler):

    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        if 'callback_query' not in update or state != 'WAIT_FOR_PIZZA_SIZE':
            return False
        return update['callback_query']['data'].startswith('size_')

    def handle(self, update: dict, state: str, order_json: dict) -> bool:
        telegram_id = update['callback_query']['from']['id']
        callback_data = update['callback_query']['data']
        pizza_size = callback_data.replace('size_', '').title()

        bot.database_client.update_user_order(telegram_id, {'pizza_size': pizza_size})
        bot.database_client.update_user_state(telegram_id, "WAIT_FOR_DRINKS")

        bot.telegram_client.answer_callback_query(update['callback_query']['id'])
        bot.telegram_client.delete_message(
            chat_id=update['callback_query']['message']['chat']['id'],
            message_id=update['callback_query']['message']['message_id'],
        )

        bot.telegram_client.send_message(
            chat_id=update['callback_query']['message']['chat']['id'],
            text="Choose drink",
            reply_markup=json_data.select_drinks
        )

        return HandlerStatus.STOP
