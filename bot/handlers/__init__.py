from aiogram import Router

from bot.handlers import (
    message_start,
    message_help,
    message_history,
    message_clean_history,
    message_stats,
    find_film,
    invalid_responce
)


def get_handlers() -> list[Router]:
    return [
        message_help.router,
        message_start.router,
        message_history.router,
        message_clean_history.router,
        message_stats.router,
        find_film.router,
        invalid_responce.router
    ]
