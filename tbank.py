# Получение баланса в ЛК Т-банка
import os
import re
from selenium.webdriver.common.by import By
from selenium_helper import SeleniumHelper
from telegram_helper import TelegramHelper
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

load_dotenv()

CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 1)
TBANK_PIN = os.environ['TBANK_PIN']
TBANK_ACCOUNT_NUMBER = os.environ['TBANK_ACCOUNT_NUMBER']

telegram = TelegramHelper()
selenium = SeleniumHelper()
driver = selenium.get_driver()

driver.get(f'https://www.tbank.ru/mybank/accounts/debit/{TBANK_ACCOUNT_NUMBER}/')

secret_code_input_list = driver.find_elements(By.XPATH, "//form[contains(@automation-id, 'pin-form')]/div//input")
if len(secret_code_input_list) > 0:
    secret_code_input_list[0].send_keys(f'{TBANK_PIN}\ue007')

# Ждем появления элемента с текстом баланса
balance_element = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located(
        (By.XPATH, "//div[@data-qa-type='balance-value']//span[contains(text(), ',') and contains(text(), '₽')]"))
)

# Ждем, пока текст в элементе не станет непустым
WebDriverWait(driver, 20).until(
    lambda _driver: balance_element.text.strip() != ''
)

balance = int(float(re.sub(r'\D', '', balance_element.text)) / 100)
cashback_element = driver.find_element(By.XPATH, "//span[@data-qa-type='cashback-badge']//span[contains(text(), '₽')]")
cashback = int(re.sub(r'\D', '', cashback_element.text))

telegram.send_message(CHAT_ID, f"""🟡 Т-Банк
Баланс: {balance}
Кешбэк: {cashback}
""")
driver.quit()
