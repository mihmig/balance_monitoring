import os
from pydoc import html

import requests


class TelegramHelper:
    def __init__(self):
        self.token = os.environ['TELEGRAM_BOT_TOKEN']

    def __del__(self):
        print("TelegramHelper: closing")

    def send_message(self, chat_id: int, text: str, buttons: list = None) -> int:
        if buttons is None:
            json_data = {
                'chat_id': chat_id,
                'text': html.escape(text),
                'parse_mode': 'html'
            }
        else:
            keyboard = list(map(lambda b: {"text": b[0], "url": b[1]}, buttons))
            # keyboard = []
            # for b in buttons:
            #     keyboard.append({"text": b[0], "url": b[1]})
            json_data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'html',
                'reply_markup': {
                    'inline_keyboard': [keyboard]
                }
            }
        response = requests.post(f'https://api.telegram.org/bot{self.token}/sendMessage', json=json_data)
        if response.status_code != 200:
            raise ValueError(f'Ошибка отправки сообщения в Телеграм: {response.status_code} {response.text}')
        j = response.json()
        if 'ok' not in j:
            raise ValueError(f'Ошибка отправки сообщения в Телеграм: {response.text}')
        if not j['ok']:
            raise ValueError(f"Ошибка отправки сообщения в Телеграм: {j['error_code']} {j['description']}")
        return j['result']['message_id']