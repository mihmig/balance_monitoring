# Вход в ЛК Мегафон-бизнес (https://b2blk.megafon.ru/soho/login).
# Отправка информации о балансе текущих остатках в Телеграм

import re
import logging
import sys

import yaml

from plugins.db_sqlite import Db
from retrying import retry
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from collections import namedtuple
from selenium_helper import SeleniumHelper
from telegram_helper import TelegramHelper

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if len(sys.argv) != 2:
    print(f'usage: python3 {__file__} config.yml')
    quit(-1)
with open('config/' + sys.argv[1], mode="r", encoding="utf-8") as file:
    config = yaml.load(file, Loader=yaml.loader.SafeLoader)

db_config = {
    'file': 'data/megafon_corp.db',
    'ddl': [
        """
            CREATE TABLE IF NOT EXISTS balance (
                phone TEXT PRIMARY KEY,
                balance REAL
            );
        """
    ]
}

db = Db(db_config)
BalanceData = namedtuple('BalanceData', 'current_balance current_moment expenses_period expenses legend')


tg_helper = TelegramHelper({'bot_token': config['bot_token']})
selenium_helper = SeleniumHelper({'headless': config['headless']}, tg_helper)
webdriver = selenium_helper.get_driver()


@retry(stop_max_attempt_number=3, wait_fixed=10000)
def login(driver: WebDriver, config: dict):
    driver.get(config['login_url'])
    login_element = driver.find_element(By.ID, ":r0:")
    login_element.send_keys(config['login'])
    password_element = driver.find_element(By.ID, ":r1:")
    password_element.send_keys(config['password'])
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    driver.find_element(By.XPATH, '//div[contains(@class,"tab-menu-item-container")]')


@retry(stop_max_attempt_number=3, wait_fixed=10000)
def get_info(driver: WebDriver) -> BalanceData:
    # После успешного логина сейчас автоматически происходит переход на искомую https://b2blk.megafon.ru/dashboard
    current_balance = driver.find_element(By.XPATH,  '//div[contains(@class,"widget-personal-account__current-balance")]//div[contains(@class,"widget-personal-account__balance-text")]').text
    current_moment = driver.find_element(By.XPATH,  '//span[contains(@class,"widget-personal-account__balance-date")]').text

    expenses_period = driver.find_element(By.XPATH, '//div[contains(@class,"widget__date-range")]').text.lower()
    expenses = driver.find_element(By.XPATH, '//li[contains(@class,"react-multi-carousel-item--active")]//div[contains(@class,"chart-pie__diagram")]//span[contains(@class,"chart__title")]').text

    legend = driver.find_elements(By.XPATH, '//li[contains(@class,"react-multi-carousel-item--active")]//div[contains(@class, "chart-pie__legend")]')
    legend = legend[0].text if len(legend) else "Расходы не найдены"

    return BalanceData(current_balance, current_moment, expenses_period, expenses, legend)


try:
    login(webdriver, config)
    balance_data = get_info(webdriver)
    balance = re.sub(r'[^\d\.-]', '', balance_data.current_balance.replace(',', '.'))


    info = db.get_line("SELECT * FROM balance WHERE phone = ?", [config['login']])
    if info is None:
        db.execute("INSERT INTO balance (phone, balance) VALUES(?,?)", [config['login'], balance])
        delta = ""
    else:
        delta = " (" + str(round(float(balance) - info['balance'],2)) + ")"
        db.execute("UPDATE balance SET balance = ? WHERE phone = ?", [balance, config['login']])

    message = f"""Баланс лицевого счета на {balance_data.current_moment}
    {balance_data.current_balance}{delta}
    Расходы {balance_data.expenses_period}
    {balance_data.expenses}
    
    {balance_data.legend}"""

    message = re.sub("\n( )+", r'\n', message)
    message = re.sub("(\D)(\d+,\d\d)( ₽)", r'\1<b>\2</b>\3', message)

    tg_helper.send_message(config['chat_id'], message, [('Перейти в ЛК', config['login_url'])])
except Exception as e:
    logger.error(f'Error while working with webdriver: {str(e)}')
    screenshot_file_name = selenium_helper.make_screenshot()
    logger.error(screenshot_file_name)
    quit(-2)
