import json
import os
import urllib.request

from dotenv import load_dotenv
from bot.domain.messenger import Messanger

load_dotenv()


class MessangerTelegram(Messanger):

    def _make_request(self, method: str, **params) -> dict:
        json_data = json.dumps(params).encode()
        print(f"URL: {os.getenv("TELEGRAM_BASE_URI")}/{method}")
        request = urllib.request.Request(
            method="POST",
            url=f"{os.getenv("TELEGRAM_BASE_URI")}/{method}",
            data=json_data,
            headers={"Content-Type": "application/json"},
        )

        with urllib.request.urlopen(request) as response:
            response_body = response.read().decode("utf-8")
            response_json = json.loads(response_body)

            assert response_json.get("ok", False), "bad response"
            return response_json["result"]

    def get_updates(self, offset: int, **kwargs: dict) -> dict:
        return self._make_request("getUpdates", offset=offset)

    def send_message(self, chat_id: int, text: str, **kwargs: dict) -> dict:
        return self._make_request("sendMessage", chat_id=chat_id, text=text, **kwargs)

    def get_me(
        self,
    ):
        return self._make_request("getMe")

    def send_sticker(self, chat_id: int, sticker: str, **kwargs: dict) -> dict:
        return self._make_request(
            "sendSticker", chat_id=chat_id, sticker=sticker, **kwargs
        )

    def send_photo(self, chat_id: int, photo: str, **kwargs: dict) -> dict:
        return self._make_request("sendPhoto", chat_id=chat_id, photo=photo, **kwargs)

    def delete_message(self, chat_id: int, message_id: int, **kwargs: dict) -> dict:
        return self._make_request(
            "deleteMessage", chat_id=chat_id, message_id=message_id, **kwargs
        )

    def answer_callback_query(self, callback_query_id: int, **kwargs: dict) -> dict:
        return self._make_request(
            "answerCallbackQuery", callback_query_id=callback_query_id, **kwargs
        )
