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

url = 'https://azs.tatneft.ru/cabinet'
driver.get(url)

balance = ''
balance = driver.find_element(By.XPATH, "//div[contains(@class, 'card__balance')]").text
balance = balance.replace('\n', '')

spent = driver.find_element(By.XPATH, "//div[@class='status' and .//div[@class='status__spend']]")
spent_text = spent.text

telegram.send_message(CHAT_ID, f"""🟢 Татнефть-бонусы
Баланс: {balance}
{spent}
""")
driver.quit()

