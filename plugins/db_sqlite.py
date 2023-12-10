import sqlite3


class Db:
    def __init__(self, config):
        self.conn = sqlite3.connect(config['file'])
        if config.get('ddl'):
            for query in config.get('ddl'):
                self.conn.execute(query)
                self.conn.commit()

    def __row_to_dict(self, cursor, row):
        fields = [column[0] for column in cursor.description]
        return {key: value for key, value in zip(fields, row)}

    # Получение одного значения
    def get_value(self, query: str, params: list = None) -> str | None:
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        if row is None:
            return None
        return row[0]

    # Получение одного кортежа
    def get_line(self, query: str, params: list = None) -> dict | None:
        cursor = self.conn.cursor()
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)
        row = cursor.fetchone()
        if row is None:
            return None
        res = self.__row_to_dict(cursor, row)
        cursor.close()
        return res

    # Получение одного столбца
    def get_row(self, query: str, params: list = None) -> list:
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        result = list()
        for row in rows:
            result.append(row[0])
        cursor.close()
        return result

    # Получение словаря (набор id->value)
    def get_dict(self, query: str, params: list = None) -> dict:
        cursor = self.conn.cursor()
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)
        result = {}
        records = cursor.fetchall()
        for r in records:
            result[r[0]] = r[1]
        cursor.close()
        return result

    # Получение множества строк (именованные кортежи)
    def get_data(self, query: str, params: list = None) -> list:
        cursor = self.conn.cursor()
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)
        return cursor.fetchall()

    def execute(self, query: str, params: list = None) :
        if params is None:
            self.conn.execute(query)
        else:
            self.conn.execute(query, params)
        self.conn.commit()

    # Вставка, при использовании конструкции RETURNING - возвращает сгенерированное поле
    def insert(self, query: str, params: list = None) -> str | int:
        cursor = self.conn.cursor()
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)
        insert_id = cursor.lastrowid
        cursor.close()
        self.conn.commit()
        return insert_id
