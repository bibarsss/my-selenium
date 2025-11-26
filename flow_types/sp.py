# Заявление о вынесении судебного приказа 
from pathlib import Path
import sqlite3
from office_sud_kz.sp.main import run as spRun 
from flow_types.base import Type
from common.sqlite import safe_execute
from browser.browser import Browser
import unicodedata

class SpType(Type):
    def browser(self):
        return Browser(True)

    def label(self)->str:
        return 'Заявление о вынесении судебного приказа'

    def table_name(self)->str:
        return 'sp'

    def excel_map(self):
        return {
            'status': 'excel_status',
            'status_text': 'excel_status_text',
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
                        number TEXT NOT NULL, 
                        podsudnost TEXT, 
                        iin_dolzhnik TEXT NOT NULL, 
                        summaIska TEXT NOT NULL, 
                        powlina TEXT NOT NULL, 
                        sp_file_realname TEXT NOT NULL,
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
            "excel_line_number": i,
            "number": safe_get('sp_excel_number'),
            'podsudnost': safe_get('sp_excel_podsudnost'),
            "iin_dolzhnik": safe_get('sp_excel_iin_dolzhnik'),
            "summaIska": safe_get('sp_excel_summa_iska'),
            "powlina": safe_get('sp_excel_powlina'),
            "sp_file_realname": safe_get('sp_excel_file_name') + ".pdf",
            "status": safe_get('excel_status'),
            "status_text": safe_get('excel_status_text'),
            }
        
        columns = ", ".join(data.keys())
        placeholders = ", ".join([":" + key for key in data.keys()])
        query = f"INSERT INTO {self.table_name()}({columns}) VALUES ({placeholders})"

        cursor.execute(query, data)

    def _get_data(self, row) -> dict | str:
        number = row['number']

        dir = None
        for path in Path(".").rglob("*.pdf"):
            if number in unicodedata.normalize("NFC", path.name):
                dir = path.parent
                break

        if not dir:
            return 'Папка не найдена!' 

        data = {
            "iin": str(self.cfg.get('iin')).zfill(12),
            "iin_dolzhnik": str(row['iin_dolzhnik']).zfill(12),
            "phone": self.cfg.get('phone'),
            "bin": self.cfg.get('bin'),
            "number": number,
            "podsudnost": row['podsudnost'],
            "address": self.cfg.get('address'),
            "detail": self.cfg.get('detail'),
            "dir": str(dir),
            "powlina": row['powlina'],
            "summaIska": row['summaIska'],
            "powlina_file_path": str(dir / self.cfg.get('sp_powlina_file_name')),
            "sp_file_path": str(dir / self.cfg.get('sp_file_name')),
            "sp_file_realpath": str(dir / row['sp_file_realname']),
        }

        return data 

    def run(self, browser, connection, row, worker_id):
        data = self._get_data(row) 

        if type(data) is str:
            safe_execute(connection, f'''UPDATE {self.table_name()} SET 
                            status = ?, 
                            status_text = ? 
                            WHERE id = ?''', 
                            ('skipped', data, row['id']))
                
            print(f"[Worker {worker_id}] row: {row['excel_line_number']} -> skipped")
            return 

        try:
            spRun(browser, data, worker_id)
            safe_execute(connection, f'''UPDATE {self.table_name()} 
                        SET status = ?, 
                        status_text = ? 
                        WHERE id = ?
                        ''', 
                        ('success', '', row['id']))
        except Exception as e:
            safe_execute(connection, f'''UPDATE {self.table_name()} 
                        SET status = ?, 
                        status_text = ? 
                        WHERE id = ?''', 
                        ('error', str(e), row['id']))