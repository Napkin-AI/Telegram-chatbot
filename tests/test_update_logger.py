import pytest

from bot.dispatcher import Dispatcher
from bot.handlers.update_database_handler import UpdateDatabaseHandler
from tests.mocks import Mock


@pytest.mark.asyncio
async def test_update_database_execution():
    test_update = {
        "update_id": 631112444,
        "message": {
            "message_id": 91,
            "from": {
                "id": 99121,
                "is_bot": False,
                "first_name": "Arseniy",
                "username": "xNapkin",
                "language_code": "en",
            },
            "chat": {
                "id": 99121,
                "first_name": "Arseniy",
                "username": "xNapkin",
                "type": "private",
            },
            "date": 1761725864,
            "text": "Test_update_logger",
        },
    }

    persist_update_called = False

    async def persist_updates(updates: list[dict]) -> None:
        nonlocal persist_update_called
        persist_update_called = True
        assert len(updates) == 1
        assert updates[0] == test_update

    async def get_user(telegram_id: int) -> dict | None:
        assert telegram_id == 99121
        return None

    mock_storage = Mock({"persist_updates": persist_updates, "get_user": get_user})

    dispatcher = Dispatcher(mock_storage, Mock({}))
    update_logger = UpdateDatabaseHandler()
    dispatcher.add_handlers([update_logger])
    await dispatcher.dispatch(test_update)

    assert persist_update_called
