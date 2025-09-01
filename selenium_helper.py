# Вспомогательный класс для работы с библиотекой Selenium
# https://github.com/mozilla/geckodriver/releases
import os
import selenium
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver

from selenium.webdriver.firefox.options import Options


class SeleniumHelper:
    def __init__(self):
        options = Options()
        options.add_argument(f"--width={os.getenv('WIDTH', 1240)}")
        options.add_argument(f"--height={os.getenv('HEIGHT', 900)}")
        options.add_argument("-profile")
        # Указываем путь для хранения профиля
        options.add_argument(os.path.abspath(r"./firefox_profile"))
        if os.getenv('HEADLESS'):
            options.add_argument('--headless')
        driver_service = selenium.webdriver.FirefoxService(log_path=os.path.devnull)
        self.driver = selenium.webdriver.Firefox(options=options, service=driver_service)
        self.driver.implicitly_wait(30)

    def __del__(self):
        if self.driver is not None:
            self.driver.quit()

    def get_driver(self) -> WebDriver:
        return self.driver

    def make_screenshot(self) -> str:
        temp_image_file = 'data/' + datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f") + ".png"
        self.driver.save_screenshot(temp_image_file)
        self.logger.info(f'screenshot saved to {temp_image_file}')
        return temp_image_file
