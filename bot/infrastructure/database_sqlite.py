import sqlite3
import os
import json

from dotenv import load_dotenv
from bot.domain.storage import Storage

load_dotenv()


class StorageSqlite(Storage):

    def recreate_database(self) -> None:

        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                connection.execute("DROP TABLE IF EXISTS telegram_updates")
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS telegram_updates
                    (
                        id INTEGER PRIMARY KEY,
                        payload TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users
                    (
                        id INTEGER PRIMARY KEY,
                        telegram_id INTEGER NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        state TEXT DEFAULT NULL,
                        order_json TEXT DEFAULT NULL
                    )
                    """
                )

    def ensure_user_exists(self, telegram_id: int) -> None:

        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                cursor = connection.execute(
                    "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
                )
                if not cursor.fetchall():
                    connection.execute(
                        "INSERT INTO users (telegram_id) VALUES (?)", (telegram_id,)
                    )

    def clear_user_state_order(self, telegram_id: int) -> None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                connection.execute(
                    "UPDATE users SET state = NULL, order_json = NULL WHERE telegram_id = ?",
                    (telegram_id,),
                )

    def update_user_state(self, telegram_id: int, state: str) -> None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                connection.execute(
                    "UPDATE users SET state = ? WHERE telegram_id = ?",
                    (state, telegram_id),
                )

    def persist_updates(self, updates: list) -> None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                data = []
                for update in updates:
                    data.append((json.dumps(update, ensure_ascii=False, indent=4),))
                connection.executemany(
                    "INSERT INTO telegram_updates (payload) VALUES (?)", data
                )

    def get_user(self, telegram_id: int | None) -> dict | None:
        if telegram_id is None:
            return telegram_id

        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                columns = ["id", "telegram_id", "created_at", "state", "order_json"]
                cursor = connection.execute(
                    f"SELECT {', '.join(columns)} FROM users WHERE telegram_id = ?",
                    (telegram_id,),
                )

                responce = cursor.fetchone()
                if responce:
                    return {key: value for (key, value) in zip(columns, responce)}
                return None

    def update_user_order(self, telegram_id: int, order: dict) -> None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                last_order = self.get_user_order(telegram_id)
                if isinstance(last_order, str):
                    last_order = json.loads(last_order)
                if last_order is not None:
                    order = last_order | order
                connection.execute(
                    "UPDATE users SET order_json = ? WHERE telegram_id = ?",
                    (json.dumps(order, ensure_ascii=False, indent=2), telegram_id),
                )

    def get_user_order(self, telegram_id: int | None) -> dict | None:
        if telegram_id is None:
            return telegram_id

        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                cursor = connection.execute(
                    "SELECT order_json FROM users WHERE telegram_id = ?", (telegram_id,)
                )

                responce = cursor.fetchone()
                if isinstance(responce[0], str):
                    return json.loads(responce[0])
                return responce[0]
