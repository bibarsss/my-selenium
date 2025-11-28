from pathlib import Path
import shutil
import sqlite3
from flow_types.baseWithExcel import WithExcelType
import re
import unicodedata

class MoveOneFileType(WithExcelType):
    def label(self)->str:
        return 'Перемещение определенного файла'

    def table_name(self)->str:
        return 'polozhit_odin_file'

    def excel_map(self):
        return {}

    def save_to_excel(self):
        return 

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
                        search_text TEXT,
                        status TEXT DEFAULT '',
                        status_text TEXT DEFAULT ''                           
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
            'search_text': safe_get('moveonefile_excel_search_text'),
            "excel_line_number": i,
            }
        
        columns = ", ".join(data.keys())
        placeholders = ", ".join([":" + key for key in data.keys()])
        query = f"INSERT INTO {self.table_name()}({columns}) VALUES ({placeholders})"

        cursor.execute(query, data)

    def _process_rows(self, ids, worker_id):
        print(f"[Worker {worker_id}] starting...")
        connection = sqlite3.connect(self.cfg.get('db_name'), timeout=30)
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA synchronous=NORMAL;")
        connection.execute("PRAGMA busy_timeout = 5000;")
        connection.row_factory = sqlite3.Row

        placeholder = ','.join('?' * len(ids))
        rows = connection.execute(f"SELECT * FROM {self.table_name()} WHERE id in ({placeholder})", ids).fetchall()

        for row in rows:
            excel_line_number = row['excel_line_number']
            print(f"[Worker {worker_id}] row: {excel_line_number}")
            self.run(row)        

        connection.commit()
        connection.close()

    def run(self, row):
        file_name = self.cfg.get('moveonefile_file_name')
        source_file = Path(file_name)

        if not source_file.exists():
            raise FileNotFoundError(f"{file_name} does not exist in the current folder")

        for path in Path(".").rglob("*.pdf"):
            normalized_name = unicodedata.normalize("NFC", path.name)
            if row['search_text'] in normalized_name:
                target_dir = path.parent
                target_file = target_dir / source_file.name

                if target_file.exists():
                    continue

                shutil.copy2(source_file, target_file)
