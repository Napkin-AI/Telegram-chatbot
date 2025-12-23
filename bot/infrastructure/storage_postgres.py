import json
import logging
import os
import time

import asyncpg
from dotenv import load_dotenv

from bot.domain.storage import Storage

load_dotenv()

logger = logging.getLogger(__name__)


class StoragePostgres(Storage):
    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None

    async def _get_pool(self) -> asyncpg.Pool:
        """Create and return connection pool for PostgreSQL"""
        if self._pool is None:
            req_env_name = [
                "POSTGRES_HOST",
                "POSTGRES_PORT",
                "POSTGRES_USER",
                "POSTGRES_PASSWORD",
                "POSTGRES_DATABASE",
            ]

            req_env = [os.getenv(env_code) for env_code in req_env_name]

            if any(env is None for env in req_env):
                raise_str = []
                for val, name in zip(req_env, req_env_name):
                    if val is None:
                        raise_str.append(name)

                raise ValueError(
                    f"Environment variable{' is ' if len(raise_str) == 1 else 's are '} not set: [{' '.join(raise_str)}])"
                )

            host, port, user, password, database = req_env
            if port is None:
                port = 5432
            else:
                port = int(port)
            self._pool = await asyncpg.create_pool(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
            )
        return self._pool

    async def close(self) -> None:
        """Close connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def save_update(self, update: dict) -> None:
        # Do not have time to parse it in better way

        method_name = "save_update"
        sql_query = "INSERT INTO telegram_events (payload) VALUES ($1)"
        start_time = time.time()

        logger.info(f"[DB] → {method_name} - {sql_query}")

        payload = json.dumps(update, ensure_ascii=False, indent=2)
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO telegram_events (payload) VALUES ($1)", payload
                )

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise

    async def recreate_database(self) -> None:
        method_name = "recreate_database"
        start_time = time.time()

        logger.info(f"[DB] → {method_name} - DROP/CREATE TABLES")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                # TODO move sql query to const file
                # better way move it to env file for secure, but hide queries is bad for review?
                await conn.execute("DROP TABLE IF EXISTS telegram_events")
                await conn.execute("DROP TABLE IF EXISTS users")
                await conn.execute("DROP TABLE IF EXISTS query_history")
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
                        telegram_id BIGINT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS query_history
                    (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        query TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise

    async def ensure_user_exists(self, telegram_id: int) -> None:
        method_name = "ensure_user_exists"
        start_time = time.time()

        logger.info(f"[DB] → {method_name} - SELECT/INSERT users")

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

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise

    async def get_history(self, telegram_id: int) -> list[str]:
        method_name = "get_history"
        sql_query = (
            "SELECT query FROM ( "
            "SELECT query, MIN(created_at) AS first_time "
            "FROM query_history "
            "WHERE user_id = $1 "
            "GROUP BY query"
            ") AS t "
            "ORDER BY first_time"
        )

        start_time = time.time()
        logger.info(f"[DB] → {method_name} - {sql_query}")

        try:
            pool = await self._get_pool()

            async with pool.acquire() as conn:
                rows = await conn.fetch(sql_query, telegram_id)

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")

            return [row["query"] for row in rows]

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise

    async def clean_history(self, telegram_id: int) -> None:
        method_name = "clean_history"

        sql_query = "DELETE FROM query_history " "WHERE user_id = $1"

        start_time = time.time()
        logger.info(f"[DB] → {method_name} - {sql_query}")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute(sql_query, telegram_id)

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise

    async def get_stats(self, telegram_id: int) -> list[tuple[str, int]]:
        method_name = "get_stats"
        sql_query = (
            "SELECT query, COUNT(*) AS count "
            "FROM query_history "
            "WHERE user_id = $1 "
            "GROUP BY query "
            "ORDER BY count DESC, query ASC"
        )

        start_time = time.time()
        logger.info(f"[DB] → {method_name} - {sql_query}")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                rows = await conn.fetch(sql_query, telegram_id)

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")

            return [(row["query"], row["count"]) for row in rows]

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise

    async def save_user_query(self, telegram_id: int, query: str) -> None:

        method_name = "save_user_query"
        sql_query = """
            INSERT INTO query_history (user_id, query)
            VALUES ($1, $2)
        """

        start_time = time.time()

        logger.info(f"[DB] → {method_name} - {sql_query}")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute(sql_query, telegram_id, query)

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise
