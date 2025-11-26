import os
import logging
import aiohttp

from dotenv import load_dotenv
from bot.domain.messenger import Messanger

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class MessangerTelegram(Messanger):
    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _make_request(self, method: str, **params) -> dict:
        url = f"{os.getenv("TELEGRAM_BASE_URI")}/{method}"

        logger.info(f"[HTTP] → POST {method} start")

        try:
            session = await self._get_session()
            async with session.post(
                url,
                json=params,
                headers={"Content-Type": "application/json"},
            ) as response:
                response_json = await response.json()
                assert response_json["ok"] == True  # noqa: E712

                logger.info(f"[HTTP] ← POST {method} end")

                return response_json["result"]

        except Exception as e:
            logger.error(f"[HTTP] ✗ POST {method}ms - Error: {e}")
            raise e

    async def get_updates(self, offset: int, **kwargs: dict) -> dict:
        return await self._make_request("getUpdates", offset=offset)

    async def send_message(self, chat_id: int, text: str, **kwargs: dict) -> dict:
        return await self._make_request(
            "sendMessage", chat_id=chat_id, text=text, **kwargs
        )

    async def get_me(self):
        return await self._make_request("getMe")

    async def send_sticker(self, chat_id: int, sticker: str, **kwargs: dict) -> dict:
        return await self._make_request(
            "sendSticker", chat_id=chat_id, sticker=sticker, **kwargs
        )

    async def send_photo(self, chat_id: int, photo: str, **kwargs: dict) -> dict:
        return await self._make_request(
            "sendPhoto", chat_id=chat_id, photo=photo, **kwargs
        )

    async def delete_message(
        self, chat_id: int, message_id: int, **kwargs: dict
    ) -> dict:
        return await self._make_request(
            "deleteMessage", chat_id=chat_id, message_id=message_id, **kwargs
        )

    async def answer_callback_query(
        self, callback_query_id: int, **kwargs: dict
    ) -> dict:
        return await self._make_request(
            "answerCallbackQuery", callback_query_id=callback_query_id, **kwargs
        )
