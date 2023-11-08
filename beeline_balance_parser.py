# Вход в ЛК Beeline и получение информации об остатках минут и СМС.
# Отправка полученной информации в Телеграм

import os
import re
import time
import temp
import argparse
import requests
from datetime import datetime
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from retrying import retry
from selenium.webdriver.firefox.webdriver import WebDriver

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--login", dest="login", required=True, help="Login")
parser.add_argument("-p", "--password", dest="password", required=True, type=str, help="Password")
parser.add_argument("-c", "--chat", dest="chat_id", required=True, type=int, help="Telegram chat id")
parser.add_argument("-t", "--token", dest="bot_token", required=True, type=str, help="Telegram bot token")
parser.add_argument("-e", "--headless", action='store_true', dest="headless", required=False,
                    help="Enable headless mode (default)")
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


@retry(stop_max_attempt_number=3, wait_fixed=5000)
def get_data(driver: WebDriver, number: str) -> str:
    res = ""
    items = webdriver.find_elements(By.XPATH, '//div[contains(@class ,"bonuses-accums-list")]/div[contains(@class, "accum-restyle")]')

    for item in items:
        parts = item.text.split('\n')
        if "Мобильная связь" in parts[0]:
            matches = re.findall(r"\D(\d+) мин", parts[1])
            res = f"{res}\nОсталось {matches[0]} мин."
        if "SMS" in parts[0]:
            matches = re.findall(r"\D(\d+) шт", parts[1])
            res = f"{res}\nОсталось {matches[0]} SMS"
    return res

@retry(stop_max_attempt_number=10, wait_fixed=5000)
def get_number_info(driver: WebDriver, number: str, url: str) -> str:
    res = f"Номер <b>{number}:</b>\n"
    driver.get(url)
    # Ждём загрузки всех элементов страницы
    time.sleep(30)
    # WebDriverWait(webdriver, args.wait).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'status-block')]")))
    res = res + get_data(driver, number)
    return res


try:
    options = webdriver.FirefoxOptions()
    if args.headless:
        options.add_argument('--headless')
    options.add_argument("--width=1240")
    options.add_argument("--height=900")
    driverService = Service(log_path=os.path.devnull)
    webdriver = webdriver.Firefox(options=options, service=driverService)
    webdriver.implicitly_wait(args.wait)  # Время ожидания загрузки страницы, поиска элементов
except Exception as e:
    send_to_tg(47254369, f'{__file__}: Error while creating webdriver: {str(e)}')
    quit(-1)

try:

    webdriver.get("https://my.beeline.ru/login.xhtml")

    loginElement = webdriver.find_element(By.ID, "loginFormB2C:loginForm:login")
    loginElement.send_keys(args.login)
    passwordElement = webdriver.find_element(By.ID, "loginFormB2C:loginForm:passwordPwd")
    passwordElement.send_keys(args.password)
    b = webdriver.find_element(By.XPATH, "//button[contains(@id,'loginFormB2C') and not(contains(@style, 'none'))]/span")
    b.click()

    # Ждём загрузки страницы
    # time.sleep(30)
    # user_info = EC.presence_of_element_located((By.XPATH,"//div[contains(@class,'user-name')]"))
    # WebDriverWait(webdriver, args.wait).until(user_info)

    message = get_number_info(webdriver, "+7 964-296-7425", "https://my.beeline.ru/b/info/subscriberDetail.xhtml?objId=3445773686")
    message = message + "\n\n" + get_number_info(webdriver, "+7 963-200-4377", "https://my.beeline.ru/b/info/subscriberDetail.xhtml?objId=3323431140")


except Exception as e:
    send_to_tg(47254369, f'{__file__}: Error while working with webdriver: {str(e)}')
    temp_image_file = temp.tempfile() + ".png"
    webdriver.save_screenshot(temp_image_file)
    print(f'screenshot saved to {temp_image_file}')
    quit(-2)
if args.debug:
    print(message)


try:
    send_to_tg(args.chat_id, message)
except Exception as e:
    print(f'Error while sending to telegram: {str(e)}')
    quit(-3)

webdriver.close()
