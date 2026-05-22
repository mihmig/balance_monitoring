# Получение баланса в ЛК Альфа-банка
import os
from time import sleep

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium_helper import SeleniumHelper
from telegram_helper import TelegramHelper
from dotenv import load_dotenv

load_dotenv()

telegram = TelegramHelper()
selenium = SeleniumHelper()

CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
driver = selenium.get_driver()

driver.get('https://azs.tatneft.ru/cabinet')
driver.refresh()  # Необходимо обновлять страницу, иначе висит окно логина

balance = ''
balance = driver.find_element(By.XPATH, "//div[contains(@class, 'card__balance')]").text
balance = balance.replace('\n', '')

spent_period = driver.find_element(By.XPATH, "//div[@class='status']/span[contains(text(), 'Потрачено')]").text
spent = driver.find_element(By.XPATH, "//div[@class='status']/div[@class='status__spend']")
spent_sum = spent.text

telegram.send_message(CHAT_ID, f"""🟢 Татнефть-бонусы
Баланс: {balance}
{spent_period}: {spent_sum}
""")
driver.quit()

