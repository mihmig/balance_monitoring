## Мониторинг баланса и остатков различных провайдеров

### Установка firefox НЕ snap-версии
https://www.omgubuntu.co.uk/2022/04/how-to-install-firefox-deb-apt-ubuntu-22-04

### Установка на debian 12
 
 ``` bash
 apt install -y python3-venv firefox-esr
 mkdir /projects
 cd /projects 
 git clone git@github.com:mihmig/balance_monitoring.git
 cd balance_monitoring/
 mkdir .venv
 python3 -m venv .venv
 source /projects/balance_monitoring/.venv/bin/activate
 pip3 install -r requirements.txt
 ```

### Чаты

-654299108 "Романсы финансов"

### Прочие настройки

# Создаём и настраиваем профиль
# profile = FirefoxProfile(profile_path)
# profile.set_preference("browser.cache.disk.parent_directory", profile_path)
# profile.set_preference("browser.cache.offline.parent_directory", profile_path)
# profile.set_preference("browser.cache.disk.enable", True)
# profile.set_preference("browser.cache.memory.enable", True)
# profile.set_preference("browser.cache.offline.enable", True)
# profile.set_preference("network.cookie.cookieBehavior", 0)  # Принимать все cookies
