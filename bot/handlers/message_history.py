from aiogram import types, Router
from aiogram.filters import Command

from bot.domain.storage import Storage

router = Router()

@router.message(Command("history"))
async def history_handler(message: types.Message, psql_storage: Storage):
    user_id = message.from_user.id

    stats = await psql_storage.get_history(user_id)

    if not stats:
        await message.answer("История пуста.")
        return

    await message.answer("История ваших показов:\n\n" + "\n".join(stats))
