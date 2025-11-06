import os
from datetime import datetime
import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
options.add_argument(f"--width={os.getenv('WIDTH', 1240)}")
options.add_argument(f"--height={os.getenv('HEIGHT', 900)}")
options.add_argument("--profile")
# Указываем путь для хранения профиля
#options.add_argument(os.path.abspath("/data/projects/balance_monitoring/firefox_profile"))
#options.add_argument("/data/projects/balance_monitoring/firefox_profile")
options.add_argument(os.path.abspath(r"./firefox_profile"))
#if os.getenv('HEADLESS'):
# options.add_argument('--headless')
driver_service = selenium.webdriver.FirefoxService(log_path=os.path.abspath("geckodriver.log"))
driver = selenium.webdriver.Firefox(options=options, service=driver_service)
driver.implicitly_wait(30)
driver.get('https://azs.tatneft.ru/cabinet')
driver.refresh()
driver.save_screenshot(f'data/{datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")}.png')
driver.quit()
