# Вход в ЛК Мегафон-бизнес (https://b2blk.megafon.ru/soho/login).
# Отправка информации о балансе текущих остатках в Телеграм

import re
import argparse
import logging

from retrying import retry
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from selenium_helper import SeleniumHelper
from telegram_helper import TelegramHelper

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


parser = argparse.ArgumentParser()
parser.add_argument("-n", "--number", dest="number", required=True, help="Phone number")
parser.add_argument("-p", "--password", dest="password", required=True, type=str, help="Password")
parser.add_argument("-c", "--chat", dest="chat_id", required=True, type=int, help="Telegram chat id")
parser.add_argument("-e", "--headless", action='store_true', dest="headless", required=False,
                    help="Enable headless mode (default)")
parser.add_argument("-t", "--token", dest="bot_token", required=True, type=str, help="Telegram bot token")
parser.add_argument("-d", "--debug", action='store_true', dest="debug", required=False, default=False,
                    help="Enable debug (default: False)")
parser.add_argument("-w", "--wait", dest="wait", required=False, type=int, default=30,
                    help="Wait timeout in seconds (default: 30)")
args = parser.parse_args()
tg_helper = TelegramHelper({'bot_token': args.bot_token})
selenium_helper = SeleniumHelper({'headless': args.headless}, tg_helper)
webdriver = selenium_helper.get_driver();


@retry(stop_max_attempt_number=3, wait_fixed=10000)
def login(driver: WebDriver):
    driver.get("https://b2blk.megafon.ru/soho/login")
    login_element = driver.find_element(By.ID, ":r0:")
    login_element.send_keys(args.number)
    password_element = driver.find_element(By.ID, ":r1:")
    password_element.send_keys(args.password)
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    driver.find_element(By.XPATH, '//div[contains(@class,"tab-menu-item-container")]')


@retry(stop_max_attempt_number=3, wait_fixed=10000)
def get_info(driver: WebDriver) -> str:
    # https://b2blk.megafon.ru/dashboard
    current_balance = driver.find_element(By.XPATH,  '//div[contains(@class,"widget-personal-account__current-balance")]//div[contains(@class,"widget-personal-account__balance-text")]').text
    current_moment_element = driver.find_element(By.XPATH,  '//span[contains(@class,"widget-personal-account__balance-date")]').text

    expenses_period = driver.find_element(By.XPATH, '//div[contains(@class,"widget__date-range")]').text
    expenses_total = driver.find_element(By.XPATH, '//li[contains(@class,"react-multi-carousel-item--active")]//div[contains(@class,"chart-pie__diagram")]//span[contains(@class,"chart__title")]').text

    legend = driver.find_elements(By.XPATH, '//li[contains(@class,"react-multi-carousel-item--active")]//div[contains(@class, "chart-pie__legendzzz")]')
    if len(legend):
        analytics = legend[0].text
    else:
        analytics = "Аналитика не найдена"

    return f"""
    Баланс лицевого счета на {current_moment_element}
    {current_balance}
    Расходы {expenses_period}
    {expenses_total}
    
    {analytics}
    """


try:
    login(webdriver)
    message = get_info(webdriver)
    message = re.sub("\n( )+", r'\n', message)
    message = re.sub("(\D)(\d+,\d\d)( ₽)", r'\1<b>\2</b>\3', message)
    if args.debug:
        print(message)
    tg_helper.send_message(args.chat_id, message, [('Перейти в ЛК', 'https://b2blk.megafon.ru/login')])
except Exception as e:
    logger.error(f'Error while working with webdriver: {str(e)}')
    screenshot_file_name = selenium_helper.make_screenshot()
    logger.error(screenshot_file_name)
    quit(-2)

# subscription_fee = webdriver.find_element(By.XPATH, '//li[contains(@class,"react-multi-carousel-item--active")]//div[contains(text(), "Абонентская плата")]/parent::div/following-sibling::div[contains(@class, "legend__price")]').text
# home_traffic = webdriver.find_element(By.XPATH, '//li[contains(@class,"react-multi-carousel-item--active")]//div[contains(text(), "Трафик в домашнем регионе")]/parent::div/following-sibling::div[contains(@class, "legend__price")]').text
# additional_services = webdriver.find_element(By.XPATH, '//li[contains(@class,"react-multi-carousel-item--active")]//div[contains(text(), "Трафик в домашнем регионе")]/parent::div/following-sibling::div[contains(@class, "legend__price")]').text
