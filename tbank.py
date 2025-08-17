# Получение баланса в ЛК Т-банка
import os
from time import sleep
from selenium.webdriver.common.by import By
from selenium_helper import SeleniumHelper
from telegram_helper import TelegramHelper

telegram = TelegramHelper()
selenium = SeleniumHelper()

CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 1)

driver = selenium.get_driver()

account_url = 'https://www.tbank.ru/mybank/accounts/debit/5402688633/'
driver.get(account_url)

# Баланс появляется не сразу
balance = ''
attempts = 0
while balance == '' and attempts < 5:
    balance = driver.find_element(By.XPATH, "//div[@data-qa-type='balance-value']//span[contains(text(), ',') and contains(text(), '₽')]").text
    attempts += 1
    sleep(1)
cashback = driver.find_element(By.XPATH, "//span[@data-qa-type='cashback-badge']//span[contains(text(), '₽')]").text

telegram.send_message(CHAT_ID, f"""🟡 Т-Банк
Баланс: {balance}
Кешбэк: {cashback}
""")
driver.quit()

