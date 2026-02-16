from pathlib import Path
import sqlite3
import time
from office_sud_kz.iskstatus.main import run as iskstatusRun
from flow_types.baseWithExcel import WithExcelType
from common.sqlite import safe_execute

class IskstatusType(WithExcelType):
    def label(self)->str:
        return 'ИСК - проверка статуса'

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
            'result_text': 'iskstatus_excel_result_text',
            'result_otvet4ik_iin': 'iskstatus_excel_result_otvet4ik_iin',
            'result_otvet4ik_name': 'iskstatus_excel_result_otvet4ik_name',
            'result_oblast': 'iskstatus_excel_result_oblast',
            'result_sud': 'iskstatus_excel_result_sud',
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
                        result_text TEXT,
                        result_otvet4ik_iin TEXT,
                        result_otvet4ik_name TEXT,
                        result_oblast TEXT,
                        result_sud TEXT,
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

    def _get_data(self, row):
        data = {
            "talon": row['talon'],
        }

        return data

    def run(self, browser, connection, row, worker_id):
        data = self._get_data(row)
        try:
            parsed_data = iskstatusRun(browser, data, worker_id)
            safe_execute(connection, f'''UPDATE {self.table_name()}
                        SET status = ?,
                        status_text = ?,
                        result = ?,
                        result_date = ?,
                        result_sud_name = ?,
                        result_number = ?,
                        result_text = ?,
                        result_otvet4ik_iin = ?,
                        result_otvet4ik_name = ?,
                        result_oblast = ?,
                        result_sud = ?
                        WHERE id = ?
                        ''',
                        ('success',
                        '',
                        parsed_data['result'],
                        parsed_data['result_date'],
                        parsed_data['result_sud_name'],
                        parsed_data['result_number'],
                        parsed_data['result_text'],
                        parsed_data['result_otvet4ik_iin'],
                        parsed_data['result_otvet4ik_name'],
                        parsed_data['result_oblast'],
                        parsed_data['result_sud'],
                        row['id']),)
        except Exception as e:
            safe_execute(connection, f"UPDATE {self.table_name()} SET status = ?, status_text = ? WHERE id = ?", ('error', str(e), row['id']))
