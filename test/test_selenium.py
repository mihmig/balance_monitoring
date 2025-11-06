import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

# Настройки окна
options = Options()
options.add_argument(f"--width={os.getenv('WIDTH', '1240')}")
options.add_argument(f"--height={os.getenv('HEIGHT', '900')}")

# HEADLESS режим
# if os.getenv('HEADLESS', '1') in ('1', 'true', 'True'):
#     options.add_argument('--headless')

firefox_profile = webdriver.FirefoxProfile(os.path.abspath("./firefox_profile"))
options.profile = firefox_profile

# Лог драйвера
service = Service(log_path=os.path.abspath("geckodriver.log"))

# Запуск браузера
driver = webdriver.Firefox(options=options, service=service)
driver.implicitly_wait(30)

# Тест-запрос
driver.get("https://azs.tatneft.ru/cabinet")
driver.save_screenshot(f"data/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')}.png")
driver.quit()