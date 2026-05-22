# Вспомогательный класс для работы с библиотекой Selenium
# https://github.com/mozilla/geckodriver/releases
import os
import shutil
import selenium
from datetime import datetime
from selenium import webdriver
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import WebDriverException


class SeleniumHelper:
    def __init__(self):
        options = Options()
        options.add_argument(f"--width={os.getenv('WIDTH', 1240)}")
        options.add_argument(f"--height={os.getenv('HEIGHT', 900)}")

        firefox_profile = FirefoxProfile(os.path.abspath(r"data/tatneft_me"))
        options.profile = firefox_profile
        # options.add_argument("-profile")
        # options.add_argument(os.path.abspath(r"./tatneft_me"))

        if os.getenv('HEADLESS', '1') in ('1', 'true', 'True'):
            options.add_argument('--headless')
        # driver_service = selenium.webdriver.FirefoxService(log_path=os.path.devnull)
        # Настройка логирования для диагностики
        log_path = os.path.abspath("geckodriver.log")
        driver_service = Service(log_path=log_path)

        self.driver = selenium.webdriver.Firefox(options=options, service=driver_service)
        self.driver.implicitly_wait(30)

    def __del__(self):
        # Закрываем драйвер безопасно
        try:
            if hasattr(self, "driver") and self.driver is not None:
                self.driver.quit()
        except Exception:
            pass

    def get_driver(self) -> WebDriver:
        return self.driver

    def make_screenshot(self) -> str:
        temp_image_file = 'data/' + datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f") + ".png"
        self.driver.save_screenshot(temp_image_file)
        self.logger.info(f'screenshot saved to {temp_image_file}')
        return temp_image_file
