import sqlite3
from common.sqlite import safe_execute
from flow_types.base import Type

class WithoutExcelType(Type):
    def label(self) -> str:
        pass

    def start(self):
        pass

    def insert(self, data, cursor: sqlite3.Cursor):
        columns = ", ".join(data.keys())
        placeholders = ", ".join([":" + key for key in data.keys()])
        query = f"INSERT INTO {self.table_name()}({columns}) VALUES ({placeholders})"
        cursor.execute(query, data)

    def update(self, row_id, data, connection):
        set_clause = ", ".join([f"{key} = :{key}" for key in data.keys()])
        query = f"UPDATE {self.table_name()} SET {set_clause} WHERE id = :id"
        params = data.copy()
        params["id"] = row_id
        safe_execute(connection, query, params)
