import pytest

from bot.dispatcher import Dispatcher
from bot.handlers.pizza_handlers.message_start_handler import MessageStartHandler
from tests.mocks import Mock
from bot.domain.order_state import OrderState


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
            "text": "/startfake",
        },
    }

    user_state = None

    async def upd_user_state(tg_id: int, state: OrderState):
        nonlocal user_state
        assert tg_id == 99121
        user_state = state

    async def clear_user_state_order(args):
        print("Clear_user_state_order passed")

    async def get_user(tg_id):
        return None

    mock_storage = Mock(
        {
            "clear_user_state_order": clear_user_state_order,
            "get_user": get_user,
            "update_user_state": upd_user_state,
        }
    )

    async def send_message(chat_id: int, text: str, **kwargs: dict) -> None:
        assert chat_id == 99121
        assert "pizza" in text.lower()
        assert "reply_markup" in kwargs
        return None

    mock_messanger = Mock({"send_message": send_message})

    dispatcher = Dispatcher(mock_storage, mock_messanger)
    start_handler = MessageStartHandler()
    dispatcher.add_handlers([start_handler])

    test_update["message"]["text"] = "start"
    assert not start_handler.can_handle(
        test_update, "Any", {}, Mock({}), Mock({})
    ), "Handler can handle incorrect update"

    test_update["message"]["text"] = "/start"
    assert start_handler.can_handle(
        test_update, "Any", {}, Mock({}), Mock({})
    ), "Handler can not handle correct update"

    await dispatcher.dispatch(test_update)

    assert user_state == "WAIT_FOR_PIZZA_NAME"
