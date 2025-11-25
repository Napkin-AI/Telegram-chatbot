import json
import os
import logging

import asyncpg
from dotenv import load_dotenv

from bot.domain.order_state import OrderState
from bot.domain.storage import Storage

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s.%(msecs)03d] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class StoragePostgres(Storage):

    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None

    async def _get_pool(self) -> asyncpg.Pool:
        """Создать и вернуть connection pool для PostgreSQL."""
        if self._pool is None:
            host = os.getenv("POSTGRES_HOST")
            port = os.getenv("POSTGRES_PORT")
            user = os.getenv("POSTGRES_USER")
            password = os.getenv("POSTGRES_PASSWORD")
            database = os.getenv("POSTGRES_DATABASE")

            if host is None:
                raise ValueError("POSTGRES_HOST environment variable is not set")
            if port is None:
                raise ValueError("POSTGRES_PORT environment variable is not set")
            if user is None:
                raise ValueError("POSTGRES_USER environment variable is not set")
            if password is None:
                raise ValueError("POSTGRES_PASSWORD environment variable is not set")
            if database is None:
                raise ValueError("POSTGRES_DATABASE environment variable is not set")

            self._pool = await asyncpg.create_pool(
                host=host,
                port=int(port),
                user=user,
                password=password,
                database=database,
            )
        return self._pool

    async def close(self) -> None:
        """Закрыть connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def persist_update(self, update: dict) -> None:
        logger.info("[DB] → persist_update start")

        payload = json.dumps(update, ensure_ascii=False, indent=2)

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO telegram_events (payload) VALUES ($1)", payload
                )

            logger.info("[DB] → persist_update done")
        except Exception as e:
            logger.info(f"[DB] → persist_update Error: {e}")
            raise e

    async def persist_updates(self, updates: list) -> None:
        for update in updates:
            await self.persist_update(update)

    async def update_user_order(self, telegram_id: int, order: dict) -> None:
        logger.info("[DB] → update_user_order start")

        try:
            pool = await self._get_pool()
            last_order = await self.get_user_order(telegram_id)
            if isinstance(last_order, str):
                last_order = json.loads(last_order)
            if last_order is not None:
                order = last_order | order

            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET order_json = $1 WHERE telegram_id = $2",
                    json.dumps(order, ensure_ascii=False, indent=2),
                    telegram_id,
                )

            logger.info("[DB] → update_user_order end")
        except Exception as e:
            logger.info(f"[DB] → update_user_order Error: {e}")
            raise e

    async def recreate_database(self) -> None:
        logger.info("[DB] → recreate_database start")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute("DROP TABLE IF EXISTS telegram_events")
                await conn.execute("DROP TABLE IF EXISTS users")
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS telegram_events
                    (
                        id SERIAL PRIMARY KEY,
                        payload TEXT NOT NULL
                    )
                    """
                )
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users
                    (
                        id SERIAL PRIMARY KEY,
                        telegram_id BIGINT NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        state TEXT DEFAULT NULL,
                        order_json TEXT DEFAULT NULL
                    )
                    """
                )

            logger.info("[DB] → recreate_database end")
        except Exception as e:
            logger.info(f"[DB] → recreate_database Error {e}")
            raise e

    async def get_user(self, telegram_id: int) -> dict | None:
        logger.info("[DB] → get_user start")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                result = await conn.fetchrow(
                    "SELECT id, telegram_id, created_at, state, order_json FROM users WHERE telegram_id = $1",
                    telegram_id,
                )
                if result:
                    user_data = {
                        "id": result["id"],
                        "telegram_id": result["telegram_id"],
                        "created_at": result["created_at"],
                        "state": result["state"],
                        "order_json": result["order_json"],
                    }
                    logger.info("[DB] → get_user end")
                    return user_data
                logger.info("[DB] → get_user end")
                return None
        except Exception as e:
            logger.info(f"[DB] → get_user Error: {e}")
            raise e

    async def get_user_order(self, telegram_id: int | None) -> dict | None:
        if telegram_id is None:
            return telegram_id

        result = await self.get_user(telegram_id)
        if (not result) or (not result.get("order_json")):
            return None

        return json.loads(result["order_json"])

    async def clear_user_state_order(self, telegram_id: int) -> None:
        logger.info("[DB] → clear_user_state_order start")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET state = NULL, order_json = NULL WHERE telegram_id = $1",
                    telegram_id,
                )

            logger.info("[DB] → clear_user_state_order end")
        except Exception as e:
            logger.info(f"[DB] → clear_user_state_order Error: {e}")
            raise e

    async def update_user_state(self, telegram_id: int, state: OrderState) -> None:
        logger.info("[DB] → update_user_state start")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET state = $1 WHERE telegram_id = $2",
                    state,
                    telegram_id,
                )

            logger.info("[DB] → update_user_state end")
        except Exception as e:
            logger.info(f"[DB] → update_user_state Error: {e}")
            raise e

    async def ensure_user_exists(self, telegram_id: int) -> None:
        logger.info("[DB] → ensure_user_exists start")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                result = await conn.fetchrow(
                    "SELECT 1 FROM users WHERE telegram_id = $1",
                    telegram_id,
                )

                if result is None:
                    await conn.execute(
                        "INSERT INTO users (telegram_id) VALUES ($1)",
                        telegram_id,
                    )

            logger.info("[DB] → ensure_user_exists end")
        except Exception as e:
            logger.info(f"[DB] → ensure_user_exists Error: {e}")
            raise e
