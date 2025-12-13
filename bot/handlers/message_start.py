from aiogram import types, Router
from aiogram.filters import Command


router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id

    welcome_text = (
        "Привет! ❤ ▲●□ "
        "Я помогу тебе найти фильмы и сериалы.\n"
        "Для поиска просто отправь название фильма или сериала.\n"
        "Напиши /help, чтобы увидеть доступные команды.\n"
    )
    await message.answer(welcome_text)
