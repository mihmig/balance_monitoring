# Вспомогательный класс для работы с библиотекой Selenium
import os
import selenium
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.service import Service


def create_webdriver(options: list) -> WebDriver:
    webdriver_options = selenium.webdriver.FirefoxOptions()
    if options.get('headless'):
        webdriver_options.add_argument('--headless')
    webdriver_options.add_argument("--width=1240")
    webdriver_options.add_argument("--height=900")
    driver_service = Service(log_path=os.path.devnull)
    webdriver = selenium.webdriver.Firefox(options=webdriver_options, service=driver_service)
    # Время ожидания загрузки страницы, поиска элементов
    webdriver.implicitly_wait(30)
    return webdriver


def make_screenshot(webdriver1: WebDriver):
    temp_image_file = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f") + ".png"
    webdriver1.save_screenshot(temp_image_file)
    print(f'screenshot saved to {temp_image_file}')
