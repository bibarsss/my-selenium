from pathlib import Path
import unicodedata
import sqlite3
from common.sqlite import safe_execute
from office_sud_kz.isk.main import run as iskRun
from flow_types.base import Type

class IskType(Type):
    def label(self)->str:
        return 'ИСК'

    def table_name(self)->str:
        return 'isk'

    def excel_map(self):
        return {
            'status': 'excel_status',
            'status_text': 'excel_status_text' 
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
                        iin_otvet4ik TEXT NOT NULL, 
                        number TEXT NOT NULL, 
                        phone_otvet4ik TEXT NOT NULL, 
                        podsudnost TEXT NOT NULL, 
                        summaIska TEXT NOT NULL, 
                        powlina TEXT NOT NULL, 
                        isk_file_realname TEXT NOT NULL,
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
            "number": safe_get('isk_excel_number'),
            "phone_otvet4ik": safe_get('isk_excel_phone_otvet4ik'),
            "podsudnost": safe_get('isk_excel_podsudnost'),
            "iin_otvet4ik": safe_get('isk_excel_iin_otvet4ik'),
            "summaIska": safe_get('isk_excel_summa_iska'),
            "powlina": safe_get('isk_excel_powlina'),
            "isk_file_realname": safe_get('isk_excel_file_name') + ".pdf",
            "status": safe_get('excel_status'),
            "status_text": safe_get('excel_status_text'),
            "excel_line_number": i,
        }

        if not all(v is not None and v != 'None' for k, v in data.items() if k not in ['status', 'status_text']):
            return

        columns = ", ".join(data.keys())
        placeholders = ", ".join([":" + key for key in data.keys()])
        query = f"INSERT INTO {self.table_name()}({columns}) VALUES ({placeholders})"

        cursor.execute(query, data)

    def _get_data(self, row) -> dict | str:
        iin = str(row['iin_otvet4ik']).zfill(12)

        dir = None
        for path in Path(".").rglob("*.pdf"):
            if iin in unicodedata.normalize("NFC", path.name):
                dir = path.parent
                break

        if not dir:
            return 'Папка не найдена!' 
            
        data = {
            "iin": str(self.cfg.get('iin')).zfill(12),
            "bin": self.cfg.get('bin'),
            "phone": self.cfg.get('phone'),
            "address": self.cfg.get('address'),
            "detail": self.cfg.get('detail'),
            "number": row['number'] ,
            "dir": str(dir),
            "phone_otvet4ik": row['phone_otvet4ik'],
            "podsudnost": row['podsudnost'],
            "iin_otvet4ik": iin,
            "summaIska": row['summaIska'],
            "powlina": row['powlina'],
            "powlina_file_path": str(dir / self.cfg.get('isk_powlina_file_name')),
            "isk_file_path": str(dir / self.cfg.get('isk_file_name')),
            "isk_file_realpath": str(dir / row['isk_file_realname']),
        }

        return data 

    def run(self, browser, connection, row, worker_id):
        data = self._get_data(row)
        if type(data) is str:
            safe_execute(connection, f"UPDATE {self.table_name()} SET status = ?, status_text = ? WHERE id = ?", ('skipped', data, row['id']))
            print(f"[Worker {worker_id}] row: {row['excel_line_number']} -> skipped")
            return 

        while True:
            try:
                iskRun(browser, data, worker_id)
                safe_execute(connection, f"UPDATE {self.table_name()} SET status = ?, status_text = ? WHERE id = ?", ('success', '', row['id']))
            except Exception as e:
                safe_execute(connection, f"UPDATE {self.table_name()} SET status = ?, status_text = ? WHERE id = ?", ('error', str(e), row['id']))
            break