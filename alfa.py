# Получение баланса в ЛК Альфа-банка
import os
from time import sleep

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium_helper import SeleniumHelper
from telegram_helper import TelegramHelper

telegram = TelegramHelper()
selenium = SeleniumHelper()

CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 47254369)
ALFA_PIN = os.environ['ALFA_PIN']
driver = selenium.get_driver()

url = 'https://web.alfabank.ru/dashboard'
driver.get(url)

secret_code_input_list = driver.find_elements(By.XPATH, "//input[contains(@aria-label, 'Введите секретный код')]")
if len(secret_code_input_list) > 0:
    secret_code_input_list[0].send_keys(f'{ALFA_PIN}\ue007')

balance = ''
attempts = 0
while balance == '' and attempts < 5:
    balance = driver.find_element(By.XPATH, "//span[contains(@data-test-id, 'common-balance-button-core-amount-title')]").text
    attempts += 1
    sleep(1)
balance = balance.replace('\n', '')
telegram.send_message(CHAT_ID, f"""🔴 Альфа-Банк
Баланс: {balance}
""")
driver.quit()

