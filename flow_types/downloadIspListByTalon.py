# Cкачиванием файлов с ск
import sqlite3
from office_sud_kz.downloadIspListByTalon.main import run as runMain 
from flow_types.baseWithExcel import WithExcelType
from common.sqlite import safe_execute
from browser.browser import Browser

class DownloadIspListByTalonType(WithExcelType):
    def browser(self):
        return Browser(with_gui=False)

    def label(self)->str:
        return 'Cкачиванием файлов с ск'

    def table_name(self)->str:
        return 'download_isp_list_by_talon'

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
                        talon TEXT, 
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
            "talon": str(row[self.cfg.index('download_ispol_list_excel_talon')].value),
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

    def _get_data(self, row) -> dict | str:
        data = {
            "talon": row['talon'],
        }

        return data 

    def run(self, browser, connection, row, worker_id):
        data = self._get_data(row) 

        try:
            runMain(browser, data, worker_id)
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