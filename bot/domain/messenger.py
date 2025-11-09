from abc import ABC, abstractmethod


class Messanger(ABC):
    @abstractmethod
    def send_message(self, chat_id: int, text: str, **kwargs: dict) -> dict:
        pass

    @abstractmethod
    def get_updates(
        self,
    ) -> dict:
        pass

    @abstractmethod
    def answer_callback_query(self, callback_query_id: int, **kwargs: dict) -> dict:
        pass

    @abstractmethod
    def delete_message(self, chat_id: int, message_id: int, **kwargs: dict) -> dict:
        pass
