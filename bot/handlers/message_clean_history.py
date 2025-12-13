from aiogram import types, Router
from aiogram.filters import Command
from bot.domain.storage import Storage


router = Router()

@router.message(Command("clean_history"))
async def stats_handler(message: types.Message, psql_storage: Storage):
      user_id = message.from_user.id

      if psql_storage is None:
            raise ValueError("Database was not configurated. Please, add it to dispatcher data")

      await psql_storage.clean_history(user_id),
      await message.answer("История была удалена")
