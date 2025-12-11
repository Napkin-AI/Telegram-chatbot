import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, Update
from aiogram.utils.serialization import deserialize_telegram_object_to_python
import dotenv

dotenv.load_dotenv()

dispatcher = Dispatcher()


@dispatcher.update.outer_middleware()
async def logger_middleware(handler: callable, event: Update, data: dict):
    payload = deserialize_telegram_object_to_python(event)

    # print(json.dumps(payload, ensure_ascii=False, indent=2))

    print(f"update_id: {payload['update_id']}")
    if "message" in payload:
        dct = payload["message"]
        print(f"message_id: {dct['message_id']}")
        if "chat" in dct:
            print(f"chat_id: {dct['chat']['id']}")
            print(f"username: {dct['chat']['username']}")

    return await handler(event, data)


@dispatcher.message(F.text)
async def massage_handler(message: Message):
    await message.answer(message.text)


@dispatcher.message(F.photo)
async def photo_handler(message: Message):
    await message.answer_photo(message.photo[-1].file_id)


async def main() -> None:
    token = os.getenv("TOKEN")
    bot = Bot(token=token)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
