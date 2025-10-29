# ходатайство 
from pathlib import Path
import unicodedata
import sqlite3
from office_sud_kz.application.main import run as applicationRun
from flow_types.base import Type
from common.sqlite import safe_execute

class ApplicationType(Type):
    def label(self)->str:
        return 'Ходатайство'

    def table_name(self)->str:
        return 'application'

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
                        iin TEXT,
                        podsudnost TEXT, 
                        nomer_dela TEXT, 
                        otvet4ik_po_delu TEXT, 
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
            'iin': str(row[self.cfg.index('application_excel_iin')].value),
            'podsudnost': str(row[self.cfg.index('application_excel_podsudnost')].value),
            'nomer_dela': str(row[self.cfg.index('application_excel_nomer_dela')].value),
            'otvet4ik_po_delu': str(row[self.cfg.index('application_excel_otvet4ik_po_delu')].value),
            "status": safe_get('excel_status'),
            "status_text": safe_get('excel_status_text'),
            }
        
        columns = ", ".join(data.keys())
        placeholders = ", ".join([":" + key for key in data.keys()])
        query = f"INSERT INTO {self.table_name()}({columns}) VALUES ({placeholders})"

        cursor.execute(query, data)

    def _get_data(self, row) -> dict | str:
        iin = str(row['iin']).zfill(12)

        dir = None
        file_name = None
        for path in Path(".").rglob("*.pdf"):
            if iin in unicodedata.normalize("NFC", path.name):
                dir = path.parent
                file_name = path.name
                break

        if not dir or not file_name:
            return f'Папка или файл не найден!' 

        data = {
            "iin": iin,
            "podsudnost": row['podsudnost'],
            "nomer_dela": row['nomer_dela'],
            "otvet4ik_po_delu": row['otvet4ik_po_delu'],
            "address": self.cfg.get('address'),
            'istcy_po_delu': self.cfg.get('application_istcy_po_delu'),
            'dir': dir,
            "file_path": str(dir / file_name),
        }

        return data 

    def run(self, browser, connection, row, worker_id):
        data = self._get_data(row) 

        if type(data) is str:
            safe_execute(connection, f"UPDATE {self.table_name()} SET status = ?, status_text = ? WHERE id = ?", ('skipped', data, row['id']))
            print(f"[Worker {worker_id}] row: {row['excel_line_number']} -> skipped")
            return 

        try:
            applicationRun(browser, data, worker_id)
            safe_execute(connection, f'''UPDATE {self.table_name()} 
                        SET status = ?, 
                        status_text = ? 
                        WHERE id = ?
                        ''', 
                        ('success', 
                        '', 
                        row['id']),)
        except Exception as e:
            safe_execute(connection, f'''UPDATE {self.table_name()} 
                        SET status = ?, 
                        status_text = ? 
                        WHERE id = ?''', 
                        ('error', str(e), row['id']),)