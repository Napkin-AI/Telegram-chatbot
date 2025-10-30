import bot.telegram_client
import bot.database_client
from bot.handlers.handler import Handler, HandlerStatus


class FinishOrder(Handler):

    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        print(update, state, order_json, sep='\n', end='\n\n\n\n')
        if 'callback_query' not in update or state != 'WAIT_FOR_ORDER_APROVE':
            return False
        return update['callback_query']['data'].startswith('approve_')

    def handle(self, update: dict, state: str, order_json: dict) -> bool:
        telegram_id = update['callback_query']['from']['id']
        callback_data = update['callback_query']['data']

        bot.database_client.update_user_order(telegram_id, {'approved': callback_data})

        bot.telegram_client.answer_callback_query(update['callback_query']['id'])
        bot.telegram_client.delete_message(
            chat_id=update['callback_query']['message']['chat']['id'],
            message_id=update['callback_query']['message']['message_id'],
        )

        if callback_data == 'approve_restore':
            bot.telegram_client.send_message(
                chat_id=update['callback_query']['message']['chat']['id'],
                text="OK! Please, choose pizza again."
            )
            update['message'] = {
                'text': '/start',
                'chat': {
                    'id': update['callback_query']['message']['chat']['id'],
                },
                'from': {
                    'id': update['callback_query']['from']['id']
                }
            }
            return HandlerStatus.CONTINUE
        else:
            bot.database_client.update_user_state(telegram_id, "NULL")
            bot.telegram_client.send_message(
                chat_id=update['callback_query']['message']['chat']['id'],
                text=f"ORDER SUCCESSFULLY FINISHED!"
            )

        return HandlerStatus.STOP
