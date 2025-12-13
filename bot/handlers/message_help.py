from aiogram import types, Router
from aiogram.filters import Command

router = Router()

@router.message(Command("help"))
async def help_handler(message: types.Message):
    help_text = (
        "Привет! ❤ ▲●□ "
        "Я — бот, помогающий найти, где посмотреть фильм/сериал.\n\n"
        "Просто пришлите название сериала или фильма, например:\n"
        "Venom\n"
        "остров собак\n"
        "магия лунного света\n\n"
        "Команды:\n"
        "/start — окно начала работы с ботом\n"
        "/help — показать сообщение помощи\n"
        "/history — история ваших поисков\n"
        "/clean_history — очистить историю и статистику\n"
        "/stats — статистика того, какие фильмы/сериалы Вам предлагались и в каком количеством\n\n"
    )
    await message.answer(help_text)
