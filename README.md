## Мониторинг баланса и остатков различных провайдеров

### Установка firefox НЕ snap-версии
https://www.omgubuntu.co.uk/2022/04/how-to-install-firefox-deb-apt-ubuntu-22-04

### Установка на debian 12
 
 ``` bash
 apt update
 apt install -y python3-venv firefox-esr
 mkdir /projects
 cd /projects 
 git clone git@github.com:mihmig/balance_monitoring.git
 git config advice.addIgnoredFile false
 git config --global --add safe.directory ./balance_monitoring
 cd balance_monitoring/
 mkdir .venv
 python3 -m venv .venv
 source .venv/bin/activate
 pip3 install -r requirements.txt
 pip install --upgrade selenium
 HEADLESS=true python3 azs.tatneft.py
   ```
Скачать https://github.com/mozilla/geckodriver/releases

#### Установка playwright
``` bash
playwright install
playwright install-deps
```
#### Чаты

-654299108 "Романсы финансов"

#### Прочие настройки

# Создаём и настраиваем профиль
# profile = FirefoxProfile(profile_path)
# profile.set_preference("browser.cache.disk.parent_directory", profile_path)
# profile.set_preference("browser.cache.offline.parent_directory", profile_path)
# profile.set_preference("browser.cache.disk.enable", True)
# profile.set_preference("browser.cache.memory.enable", True)
# profile.set_preference("browser.cache.offline.enable", True)
# profile.set_preference("network.cookie.cookieBehavior", 0)  # Принимать все cookies


### playwright
* cd /data/projects/balance_monitoring
* source .venv/bin/activate
* pip3 install playwright
* playwright install
* (На Windows C:\Users\user\AppData\Local\ms-playwright\ На Linux /root/.cache/ms-playwright/)
* playwright install-deps (Alternatively, use apt:  apt-get install libgtk-4-1 
