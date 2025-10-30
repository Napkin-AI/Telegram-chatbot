import json
import os
import urllib.request
from dotenv import load_dotenv

load_dotenv()

def make_request(method: str, **params) -> dict:
    json_data = json.dumps(params).encode()

    request = urllib.request.Request(
        method='POST',
        url=f"{os.getenv("TELEGRAM_BASE_URI")}/{method}",
        data=json_data,
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(request) as response:
        response_body = response.read().decode('utf-8')
        response_json = json.loads(response_body)

        assert response_json.get("ok", False) == True, "bad response"
        return response_json['result']


def get_updates(offset: int) -> dict:
    return make_request('getUpdates', offset=offset)


def send_message(**kwargs) -> dict:
    print(kwargs)
    return make_request('sendMessage', **kwargs)


def get_me():
    return make_request('getMe')


def send_sticker(chat_id: int, sticker: str) -> dict:
    return make_request('sendSticker', chat_id=chat_id, sticker=sticker)

def send_photo(chat_id: int, photo: str) -> dict:
    return make_request('sendPhoto', chat_id=chat_id, photo=photo)
