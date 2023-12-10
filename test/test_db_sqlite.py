from plugins.db_sqlite import Db
import yaml
import re

config = {'login': '123'}

db_config = {
    'file': 'data/megafon_corp.db',
    'ddl': [
        """
            CREATE TABLE IF NOT EXISTS balance (
                phone TEXT PRIMARY KEY,
                balance REAL,
                expenses REAL
            );
        """
    ]
}

db = Db(db_config)
expenses = ' 235,46 Р'
expenses = re.sub(r'[^\d\.-]', '', expenses.replace(',', '.'))
info = db.get_line("SELECT * FROM balance WHERE phone = ?", [config['login']])
if info is None:
    db.execute("INSERT INTO balance (phone, balance, expenses) VALUES(?, ?)", [config['login'], expenses])
else:
    delta = str(round(float(expenses) - info['expenses'], 2))
    print(delta)
    db.execute("UPDATE balance SET expenses = ? WHERE phone = ?", [expenses, config['login']])
