from pathlib import Path
import sqlite3
from flow_types.base import Type
import re

class MoveBy2SubfolderType(Type):
    def label(self)->str:
        return 'Переместить папки через 2 подпапки'

    def table_name(self)->str:
        return 'moveby2subfolder'

    def excel_map(self):
        pass

    def migration(self):
        connection = sqlite3.connect(self.cfg.get('db_name'))
        cursor = connection.cursor()
        cursor.execute(f'''
            DROP TABLE IF EXISTS {self.table_name()} 
            ''')

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name()}(
                        id INTEGER PRIMARY KEY,
                        search_text TEXT, 
                        sud_folder_name TEXT, 
                        client_folder_name TEXT
                    )
                            ''')
        connection.commit()        
        connection.close()

    def insert(self, row: tuple, cursor: sqlite3.Cursor):
        def safe_get(column_name: str) -> str:
            try:
                idx = self.cfg.index(column_name)
                return str(row[idx].value) if row[idx].value is not None else ""
            except (ValueError, IndexError):
                return ""

        data = {
            'search_text': safe_get('moveby2subfolder_excel_search_text'),
            'sud_folder_name': safe_get('moveby2subfolder_excel_sud_folder_name'),
            'client_folder_name': safe_get('moveby2subfolder_excel_client_folder_name'),
            }
        
        columns = ", ".join(data.keys())
        placeholders = ", ".join([":" + key for key in data.keys()])
        query = f"INSERT INTO {self.table_name()}({columns}) VALUES ({placeholders})"

        cursor.execute(query, data)

    def run(self, row):
        def sanitize(name: str) -> str:
            return re.sub(r'[<>:"/\\|?*]', '', name.strip())

        main = sanitize(self.cfg.get('moveby2subfolder_main_folder_name'))
        sud = sanitize(row['sud_folder_name'])
        client = sanitize(row['client_folder_name'])

        target_dir = Path(main) / sud / client
        target_dir.mkdir(parents=True, exist_ok=True)

        for pdf in Path(".").glob("*.pdf"):
            try:
                if row['search_text'] in pdf.name:
                    target_file = target_dir / pdf.name
                    if target_file.exists():
                        pdf.unlink()
                    else:
                        pdf.rename(target_file)
            except Exception as e:
                continue
