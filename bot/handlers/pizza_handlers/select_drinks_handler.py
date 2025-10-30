import bot.telegram_client
import bot.database_client
from bot.handlers.pizza_handlers import json_data
from bot.handlers.handler import Handler, HandlerStatus


class SelectDrinks(Handler):

    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        if 'callback_query' not in update or state != 'WAIT_FOR_DRINKS':
            return False
        return update['callback_query']['data'].startswith('drink_')

    def handle(self, update: dict, state: str, order_json: dict) -> bool:
        telegram_id = update['callback_query']['from']['id']
        callback_data = update['callback_query']['data']
        drink = callback_data.replace('drink_', '').title()

        bot.database_client.update_user_order(telegram_id, {'drink': drink})
        bot.database_client.update_user_state(telegram_id, "WAIT_FOR_ORDER_APROVE")

        bot.telegram_client.answer_callback_query(update['callback_query']['id'])
        bot.telegram_client.delete_message(
            chat_id=update['callback_query']['message']['chat']['id'],
            message_id=update['callback_query']['message']['message_id'],
        )

        user_order = bot.database_client.get_user_order(telegram_id)

        if not user_order:
            bot.telegram_client.send_message(
                chat_id=update['callback_query']['message']['chat']['id'],
                text="The backet is empty! Something gone wrong!"
            )
            bot.database_client.update_user_state(telegram_id, "WAIT_FOR_PIZZA_NAME")
            return HandlerStatus.CONTINUE
        else:
            bot.telegram_client.send_message(
                chat_id=update['callback_query']['message']['chat']['id'],
                text=f"Approve order\nPizza: {user_order['pizza_name']}\nSize: {user_order['pizza_size']}\nDrink: {user_order['drink']}",
                reply_markup=json_data.approve_json
            )

        return HandlerStatus.STOP
