# Вспомогательный класс для работы с библиотекой Selenium
import os
import selenium
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver

def create_webdriver(options: list) -> WebDriver:
    driver_options = selenium.webdriver.FirefoxOptions()
    if options.get('headless'):
        driver_options.add_argument('--headless')
    driver_options.add_argument("--width=1240")
    driver_options.add_argument("--height=900")
    driver_service = selenium.webdriver.FirefoxService(log_path=os.path.devnull)
    driver = selenium.webdriver.Firefox(options=driver_options, service=driver_service)
    # Время ожидания загрузки страницы, поиска элементов
    driver.implicitly_wait(30)
    return driver


def make_screenshot(driver: WebDriver) -> str:
    temp_image_file = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f") + ".png"
    driver.save_screenshot(temp_image_file)
    print(f'screenshot saved to {temp_image_file}')
    return temp_image_file
