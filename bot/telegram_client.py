import json
import os
import urllib.request
from dotenv import load_dotenv

load_dotenv()

def makeRequest(method: str, **params) -> dict:
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


def getUpdates(offset: int) -> dict:
    return makeRequest('getUpdates', offset=offset)


def sendMessage(chat_id: int, text: int) -> dict:
    return makeRequest('sendMessage', chat_id=chat_id, text=text)


def getMe():
    return makeRequest('getMe')


def sendSticker(chat_id: int, sticker: str) -> dict:
    return makeRequest('sendSticker', chat_id=chat_id, sticker=sticker)
