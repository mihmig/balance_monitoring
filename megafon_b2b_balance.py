# Вход в ЛК Мегафон-бизнес (https://b2blk.megafon.ru/soho/login).
# Отправка информации о балансе текущих остатках в Телеграм

import os
import re
import temp
import argparse
import requests
import logging
from retrying import retry
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.webdriver import WebDriver

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


parser = argparse.ArgumentParser()
parser.add_argument("-n", "--number", dest="number", required=True, help="Phone number")
parser.add_argument("-c", "--chat", dest="chat_id", required=True, type=int, help="Telegram chat id")
parser.add_argument("-p", "--password", dest="password", required=True, type=str, help="Password")
parser.add_argument("-e", "--headless", action='store_true', dest="headless", required=False,
                    help="Enable headless mode (default)")
parser.add_argument("-t", "--token", dest="bot_token", required=True, type=str, help="Telegram bot token")
parser.add_argument("-d", "--debug", action='store_true', dest="debug", required=False, default=False,
                    help="Enable debug (default: False)")
parser.add_argument("-w", "--wait", dest="wait", required=False, type=int, default=10,
                    help="Wait timeout in seconds (default: 10)")
args = parser.parse_args()


def send_to_tg(chat_id: int, text: str):
    logger.debug(f"Отправляем в чат {chat_id} сообщение: {text}")
    json_data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'html'
    }
    requests.post('https://api.telegram.org/bot' + args.bot_token + '/sendMessage', json=json_data)

def create_web_driver() -> WebDriver:
    options = webdriver.FirefoxOptions()
    if args.headless:
        options.add_argument('--headless')
    options.add_argument("--width=1240")
    options.add_argument("--height=900")
    driverService = Service(log_path=os.path.devnull)
    driver = webdriver.Firefox(options=options, service=driverService)
    driver.implicitly_wait(args.wait)  # Время ожидания загрузки страницы, поиска элементов
    return driver


def login(driver: WebDriver):
    driver.get("https://b2blk.megafon.ru/soho/login")
    login_element = driver.find_element(By.ID, ":r0:")
    login_element.send_keys(args.number)
    password_element = driver.find_element(By.ID, ":r1:")
    password_element.send_keys(args.password)
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()


@retry(stop_max_attempt_number=3, wait_fixed=5000)
def get_info(driver: WebDriver) -> str:
    current_balance = driver.find_element(By.XPATH,  '//div[contains(@class,"widget-personal-account__current-balance")]//div[contains(@class,"widget-personal-account__balance-text")]').text
    current_moment_element = driver.find_element(By.XPATH,  '//span[contains(@class,"widget-personal-account__balance-date")]').text

    expenses_period = driver.find_element(By.XPATH, '//div[contains(@class,"widget__date-range")]').text
    expenses_total = driver.find_element(By.XPATH, '//li[contains(@class,"react-multi-carousel-item--active")]//div[contains(@class,"chart-pie__diagram")]//span[contains(@class,"chart__title")]').text

    legend = driver.find_element(By.XPATH, '//li[contains(@class,"react-multi-carousel-item--active")]//div[contains(@class, "chart-pie__legend")]').text

    message = f"""
    Баланс лицевого счета на {current_moment_element}
    {current_balance}
    Расходы {expenses_period}
    {expenses_total}
    
    {legend}
    """
    return message


try:
    driver = create_web_driver()
except Exception as e:
    send_to_tg(47254369, f'Error while creating webdriver: {str(e)}')
    quit(-1)

try:
    login(driver)
except Exception as e:
    send_to_tg(47254369, f'Error while login: {str(e)}')
    temp_image_file = temp.tempfile() + ".png"
    driver.save_screenshot(temp_image_file)
    logger.debug(f'screenshot saved to {temp_image_file}')
    quit(-2)

# Делаем несколько попыток извлечь данные со страницы (бывает, что некоторые элементы долго подгружаются)
try:
    message = get_info(driver)
except Exception as e:
    logger.error(f'Error while working with webdriver: {str(e)}')
    temp_image_file = temp.tempfile() + ".png"
    driver.save_screenshot(temp_image_file)
    logger.debug(f'screenshot saved to {temp_image_file}')
    quit(-2)

driver.close()

message = re.sub("\n( )+", r'\n', message)
message = re.sub("(\D)(\d+,\d\d)( ₽)", r'\1<b>\2</b>\3', message)

if args.debug:
    print(message)

try:
    send_to_tg(args.chat_id, message)
except Exception as e:
    logger.error(f'Error while sending to telegram: {str(e)}')
    quit(-3)


# subscription_fee = webdriver.find_element(By.XPATH, '//li[contains(@class,"react-multi-carousel-item--active")]//div[contains(text(), "Абонентская плата")]/parent::div/following-sibling::div[contains(@class, "legend__price")]').text
# home_traffic = webdriver.find_element(By.XPATH, '//li[contains(@class,"react-multi-carousel-item--active")]//div[contains(text(), "Трафик в домашнем регионе")]/parent::div/following-sibling::div[contains(@class, "legend__price")]').text
# additional_services = webdriver.find_element(By.XPATH, '//li[contains(@class,"react-multi-carousel-item--active")]//div[contains(text(), "Трафик в домашнем регионе")]/parent::div/following-sibling::div[contains(@class, "legend__price")]').text
