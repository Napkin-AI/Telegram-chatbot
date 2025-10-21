import sqlite3
import os
import json
from dotenv import load_dotenv

load_dotenv()

def recreate_database() -> None:

    with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
        with connection:
            connection.execute("DROP TABLE IF EXISTS telegram_updates")
            connection.execute("""
                CREATE TABLE IF NOT EXISTS telegram_updates
                (
                    id INTEGER PRIMARY KEY,
                    payload TEXT NOT NULL
                )
                """)


def persist_updates(updates: list) -> None:
    with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
        with connection:
            data = []
            for update in updates:
                data.append(
                    (json.dumps(update, ensure_ascii=False, indent=4), )
                )
            connection.executemany("INSERT INTO telegram_updates (payload) VALUES (?)", data)
