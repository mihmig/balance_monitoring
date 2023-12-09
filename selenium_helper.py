# Вспомогательный класс для работы с библиотекой Selenium
import logging
import os
import selenium
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver

from telegram_helper import TelegramHelper


class SeleniumHelper:
    def __init__(self, options: dict, tg_helper: TelegramHelper = None):
        self.options = options #config['bot_token']
        self.tg_helper = tg_helper
        self.logger = logging.getLogger(__name__)
        try:
            driver_options = selenium.webdriver.FirefoxOptions()
            if options.get('headless'):
                driver_options.add_argument('--headless')
            driver_options.add_argument("--width=1240")
            driver_options.add_argument("--height=900")
            driver_service = selenium.webdriver.FirefoxService(log_path=os.path.devnull)
            self.driver = selenium.webdriver.Firefox(options=driver_options, service=driver_service)
            # Время ожидания загрузки страницы, поиска элементов
            self.driver.implicitly_wait(options.get('wait') or 30)
        except Exception as e:
            tg_helper.send_message(47254369, f'{__file__}: Error while creating webdriver: {str(e)}')
            self.logger.error(e)
            if webdriver is not None:
                webdriver.quit()
            quit(-1)

    def __del__(self):
        if self.driver is not None:
            self.driver.quit()

    def get_driver(self) -> WebDriver:
        return self.driver

    def make_screenshot(self) -> str:
        temp_image_file = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f") + ".png"
        self.driver.save_screenshot(temp_image_file)
        self.logger.info(f'screenshot saved to {temp_image_file}')
        return temp_image_file
