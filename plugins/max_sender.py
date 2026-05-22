# Плагин отправки уведомлений в телеграм.
import logging
from threading import Thread

import requests
from retrying import retry


def retry_if_io_error(exception):
    print(f"error: {exception}")
    return isinstance(exception, IOError)


class MaxSender:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.send_message_url = "https://platform-api.max.ru/messages"
        self.headers = {
            "Authorization": bot_token,
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger(__name__)

    # Отправка сообщения в MAX-чат.
    @retry(retry_on_exception=retry_if_io_error, wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def send_message_with_retry(self, chat_id: int, text: str, format: str = 'html') -> None:
        self.logger.info(f'MAX: Отправляем сообщение: chat_id: {chat_id}, text: {text}')
        params = {
            "chat_id": chat_id
        }
        response = requests.post(self.send_message_url,
                                 params=params,
                                 headers=self.headers,
                                 json={"text": text, "format": format}
                                 )

        if response.status_code != 200:
            self.logger.error(f'Error: {response.status_code} {response.text}')

    # Отправка сообщения в отдельном потоке, чтобы не задерживать основной
    def send_message(self, chat_id: int, text: str):
        Thread(target=self.send_message_with_retry, args=(chat_id, text)).start()
