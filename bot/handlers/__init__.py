from bot.handlers.handler import Handler
from bot.handlers.update_database_handler import UpdateDatabaseHandler
from bot.handlers.ensure_user_exist_handler import EnsureUserExists
from bot.handlers.pizza_handlers.message_start_handler import MessageStartHandler
from bot.handlers.pizza_handlers.select_pizza_handler import SelectPizzaHandler
from bot.handlers.pizza_handlers.pizza_size_handler import SelectPizzaSize
from bot.handlers.pizza_handlers.select_drinks_handler import SelectDrinks
from bot.handlers.pizza_handlers.order_approve_handler import FinishOrder


def get_handlers() -> list[Handler]:
    return [
        UpdateDatabaseHandler(),
        EnsureUserExists(),
        FinishOrder(),
        SelectDrinks(),
        MessageStartHandler(),
        SelectPizzaHandler(),
        SelectPizzaSize(),
    ]
