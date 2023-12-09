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
 mkdir ~/.venv
 cd ~/.venv
 python3 -m venv ~/.venv
 source ~/.venv/bin/activate
 pip3 install -r requirements.txt
 ```


