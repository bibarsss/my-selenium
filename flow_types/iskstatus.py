from pathlib import Path
import unicodedata
import sqlite3
from office_sud_kz.isk.main import run as iskRun
from flow_types.base import Type

class IskstatusType(Type):
    def label(self)->str:
        return 'Иск проверка статуса'

    def table_name(self)->str:
        return 'iskstatus'

    def excel_map(self):
        return {
            'status': 'excel_status',
            'status_text': 'excel_status_text',
            'result': 'iskstatus_excel_result', 
            'result_date': 'iskstatus_excel_result_date', 
            'result_sud_name': 'iskstatus_excel_result_sud_name', 
            'result_number': 'iskstatus_excel_result_number', 
        }

    def migration(self):
        connection = sqlite3.connect(self.cfg.get('db_name'))

        cursor = connection.cursor()
        cursor.execute(f'''
            DROP TABLE IF EXISTS {self.table_name()} 
            ''')
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name()}(
                        id INTEGER PRIMARY KEY,
                        excel_line_number INTEGER,
                        talon TEXT NOT NULL, 
                        result TEXT, 
                        result_date TEXT,
                        result_sud_name TEXT, 
                        result_number TEXT,
                        status TEXT,
                        status_text TEXT                            
                    )
                            ''')
        connection.commit()        
        connection.close()


    def insert(self, row: tuple, cursor: sqlite3.Cursor, i):
        def safe_get(column_name: str) -> str:
            try:
                idx = self.cfg.index(column_name)
                return str(row[idx].value) if row[idx].value is not None else ""
            except (ValueError, IndexError):
                return ""

        data = {
            "talon": str(row[self.cfg.index('iskstatus_excel_talon')].value),
            "excel_line_number": i,
            "status": safe_get('excel_status'),
            "status_text": safe_get('excel_status_text'),
            }
        
        talon = str(data.get('talon', '')).strip()  

        if not talon.isdigit():
            return

        columns = ", ".join(data.keys())
        placeholders = ", ".join([":" + key for key in data.keys()])
        query = f"INSERT INTO {self.table_name()}({columns}) VALUES ({placeholders})"

        cursor.execute(query, data)

    def run(self, browser, data, connection, row, worker_id):
        print('run iskstatus')