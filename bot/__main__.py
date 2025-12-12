import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from bot.domain.storage import Storage
from bot.handlers import get_handlers
from bot.infrastructure.storage_postgres import StoragePostgres
from bot.middlewares.save_update_and_create_user import SaveUdpateMiddleware
from bot.middlewares.database_injection import PSQLInjection

load_dotenv()

async def main() -> None:

    storage: Storage = StoragePostgres()
    dispatcher = Dispatcher()

    async with Bot(token=os.getenv("TELEGRAM_TOKEN")) as bot:
        dispatcher.update.outer_middleware(PSQLInjection(storage))
        dispatcher.update.outer_middleware(SaveUdpateMiddleware())
        dispatcher.include_routers(*get_handlers())

        try:
            await dispatcher.start_polling(bot)
        except KeyboardInterrupt:
            print("\nBot was killed!")
        finally:
            if hasattr(storage, "close"):
                await storage.close()


if __name__ == "__main__":
    if not os.getenv("TELEGRAM_TOKEN"):
        print("TELEGRAM_TOKEN is undefined, you should add it to environment!")
        raise SystemExit(1)

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s.%(msecs)03d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    asyncio.run(main())

