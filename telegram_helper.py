import requests


class TelegramHelper:
    def __init__(self, config):
        self.token = config['bot_token']

    def __del__(self):
        print("TelegramHelper: destructuring")

    def send_message(self, chat_id: int, text: str, ) -> int:
        json_data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'html'
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