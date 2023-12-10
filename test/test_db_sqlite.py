from plugins.db_sqlite import Db
import yaml
import re

with open('config/samoilov.yml', mode="r", encoding="utf-8") as file:
    config = yaml.load(file, Loader=yaml.loader.SafeLoader)

db_config = {
    'file': 'data/megafon_corp.db',
    'ddl': [
        """
            CREATE TABLE IF NOT EXISTS balance (
                phone TEXT PRIMARY KEY,
                balance REAL
            );
        """
    ]
}

db = Db(db_config)
current_balance = '-468,450 ₽'
balance = re.sub(r'[^\d\.-]','', current_balance.replace(',', '.'))
info = db.get_line("SELECT * FROM balance WHERE phone = ?", [config['phone']])
if info is None:
    db.execute("INSERT INTO balance (phone, balance) VALUES(?,?)", [config['phone'], balance])
else:
    delta = float(balance) - info['balance']
    print(delta)
    db.execute("UPDATE balance SET balance = ? WHERE phone = ?", [balance, config['phone'] ])
