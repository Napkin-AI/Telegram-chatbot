from aiogram import types, Router
from aiogram.filters import Command
from bot.domain.storage import Storage

router = Router()


@router.message(Command("stats"))
async def stats_handler(message: types.Message, psql_storage: Storage):
    user_id = message.from_user
    if user_id is None:
        raise ValueError("Telegram API error")

    user_id = user_id.id

    stats = await psql_storage.get_stats(user_id)

    if not stats:
        await message.answer("Статистика пуста.")
        return

    lines = [f"{i+1}. {s[0]} — {s[1]} раз(а)" for i, s in enumerate(stats)]
    await message.answer("Статистика ваших показов:\n\n" + "\n".join(lines))
