# Вход в ЛК Beeline и получение информации об остатках минут и СМС.
# Отправка полученной информации в Телеграм

import re
import argparse
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.firefox.webdriver import WebDriver

from selenium_helper import create_webdriver, make_screenshot
from telegram_helper import TelegramHelper

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
thelper = TelegramHelper({'bot_token': args.bot_token})


def get_accums(driver: WebDriver) -> dict:
    items = driver.find_elements(By.XPATH, '//div[contains(@class ,"bonuses-accums-list")]/div[contains(@class, "accum-restyle")]')
    accums = {}
    for item in items:
        parts = item.text.split('\n')
        if "Мобильная связь" in parts[0]:
            matches = re.findall(r"\D(\d+) мин", parts[1])
            if len(matches):
                accums['minutes'] = matches[0]
        if "SMS" in parts[0]:
            matches = re.findall(r"\D(\d+) шт", parts[1])
            if len(matches):
                accums['sms'] = matches[0]
    return accums


def get_number_info(driver: WebDriver, number: str, url: str) -> str:
    attempts = 0
    accums = []
    while len(accums) == 0 and attempts < 5:
        driver.get(url)
        accums = get_accums(driver)
        attempts += 1
    if len(accums) == 0:
        raise ValueError(f'Не удалось извлечь информацию об остатках для номера {number}')
    res = f"Номер <b>{number}:</b>\nОсталось {accums['minutes']} мин.\nОсталось {accums['sms']} SMS"
    return res


try:
    webdriver = create_webdriver({'headless': args.headless})
except Exception as e:
    thelper.send_message(47254369, f'{__file__}: Error while creating webdriver: {str(e)}')
    logger.error(e)
    if webdriver is not None:
        webdriver.quit()
    quit(-1)

try:
    webdriver.get("https://my.beeline.ru/login.xhtml")
    loginElement = webdriver.find_element(By.ID, "loginFormB2C:loginForm:login")
    loginElement.send_keys(args.login)
    passwordElement = webdriver.find_element(By.ID, "loginFormB2C:loginForm:passwordPwd")
    passwordElement.send_keys(args.password)
    b = webdriver.find_element(By.XPATH, "//button[contains(@id,'loginFormB2C') and not(contains(@style, 'none'))]/span")
    b.click()
    # Проверка успешной аутентификации
    blocks = webdriver.find_elements(By.XPATH, "//div[contains(@class,'user-name')]")
    if len(blocks) == 0:
        raise ValueError("Не удалось войти в личный кабинет")
    numbers = {
        "+7 964-296-7425": "https://my.beeline.ru/b/info/subscriberDetail.xhtml?objId=3445773686",
        "+7 963-200-4377": "https://my.beeline.ru/b/info/subscriberDetail.xhtml?objId=3323431140"
    }

    result_list = list()
    for number, url in (numbers.items()):
        print(number, "->", url)
        result_list.append(get_number_info(webdriver, number, url))

    message = "\n\n".join(result_list)

except Exception as e:
    thelper.send_message(47254369, f'{__file__}: Error while working with webdriver: {str(e)}')
    make_screenshot(webdriver)
    webdriver.quit()
    quit(-2)

if args.debug:
    print(message)

try:
    thelper.send_message(args.chat_id, message)
except Exception as e:
    print(f'Error while sending to telegram: {str(e)}')
    webdriver.quit()
    quit(-3)

webdriver.quit()
