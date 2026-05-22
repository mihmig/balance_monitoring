import logging
from datetime import datetime
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)


class Tatneft:
    def __init__(self, config: dict):
        self.logger = logging.getLogger(__name__)
        self.user_data_dir = config['user_data_dir']
        self.headless = config.get('headless', True) == "True"
        # user_data_dir = "tatneft_me"  # Папка для профиля

    def do(self):
        # Использование context manager 'with' гарантирует корректное закрытие всего и вся
        with sync_playwright() as p:
            context = p.firefox.launch_persistent_context(self.user_data_dir, headless=self.headless)
            page = context.pages[0]
            page.goto("https://azs.tatneft.ru/cabinet")
            page.reload()  # Почему-то требуется reload (тогда cookies подхватываются)

            balance_text = page.locator(".card__balance").inner_text()
            balance_integer = balance_text.strip().split(",")[0].strip()
            self.logger.info(f"Бонусы: {balance_integer}")

            # Достаем фразу "Потрачено в %месяц%"
            status_title = page.locator(".status >> span").first.inner_text()
            # Достаем сумму
            spend_value = page.locator(".status >> .status__spend").first.inner_text()
            spend_value_clean = spend_value.replace("\xa0", " ").strip()

            self.logger.info(f"Статус: {status_title.strip()}")
            self.logger.info(f"Сумма: {spend_value_clean}")

            page.screenshot(path=f"data/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')}.png")

            # Закрываем контекст внутри блока with
            context.close()


if __name__ == "__main__":
    tatneft = Tatneft({
        'user_data_dir': 'data/tatneft_me',
        'headless': 'True'
    })
    tatneft.do()
