# Tazalau
import sqlite3
from office_sud_kz.downloadIspListByTalon.main import run as runMain
from flow_types.baseWithExcel import WithExcelType
from common.sqlite import safe_execute
from browser.browser import Browser

class TazalauType(WithExcelType):
    def label(self)->str:
        return 'Банкротство, tazalau'

    def browser(self):
        return Browser(bool(int(self.cfg.get('show_browser'))), self.download_dir())

    def download_dir(self):
        return 'downloads_tazalau'

    def table_name(self)->str:
        return 'tazalau'

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
                        data_vnesud TEXT,
                        data_sud TEXT,
                        data_vosstanovlenie TEXT,
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

        iin = str(row[self.cfg.index('tazalau_excel_iin')].value)
        if not iin.isdigit():
            return
        iin = iin.zfill(12)
        data = {
            "iin": iin,
            "excel_line_number": i,
            "status": safe_get('excel_status'),
            "status_text": safe_get('excel_status_text'),
            }

        columns = ", ".join(data.keys())
        placeholders = ", ".join([":" + key for key in data.keys()])
        query = f"INSERT INTO {self.table_name()}({columns}) VALUES ({placeholders})"

        cursor.execute(query, data)

    def _process_rows(self, ids, worker_id):
        print(f"[Worker {worker_id}] starting...")
        browser = self.browser()

        connection = sqlite3.connect(self.cfg.get('db_name'), timeout=30)
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA synchronous=NORMAL;")
        connection.execute("PRAGMA busy_timeout = 5000;")
        connection.row_factory = sqlite3.Row

        placeholder = ','.join('?' * len(ids))
        rows = connection.execute(f"SELECT * FROM {self.table_name()} WHERE id in ({placeholder})", ids).fetchall()

        for row in rows:
            if int(row['id']) % 10 == 0:
                browser.refresh()

            excel_line_number = row['excel_line_number']
            print(f"[Worker {worker_id}] row: {excel_line_number} -> start")
            self.run(browser, connection, row, worker_id)

        connection.commit()
        connection.close()
        browser.driver.quit()

    def run(self, browser, connection, row, worker_id):
        print('run')
# {'id': 27, 'excel_line_number': 28, 'iin': '901006402244', 'data_vnesud': None, 'data_sud': None, 'data_vosstanovlenie': None, 'status': '', 'status_text': ''}
        data = dict(row)
        print(data)
        # bankruptcyAndInsolvent = "https://tazalau.qoldau.kz/ru/list/bankruptcy-and-insolvent"
        # bankruptcyAndInsolventName = "Внесудебное банкротство"
        # bankruptcyAndInsolventType = 1

        # data = self._get_data(row)

        # try:
        #     runMain(browser, data, worker_id)
        #     safe_execute(connection, f'''UPDATE {self.table_name()}
        #                 SET status = ?,
        #                 status_text = ?
        #                 WHERE id = ?
        #                 ''',
        #                 ('success',
        #                 '',
        #                 row['id']),)
        # except Exception as e:
        #     safe_execute(connection, f'''UPDATE {self.table_name()}
        #                 SET status = ?,
        #                 status_text = ?
        #                 WHERE id = ?''',
        #                 ('error', str(e), row['id']),)

    def save_to_excel(self):
        print('Сохраняем на эксель файл...')
        print('daje daje')
        # base, ext = os.path.splitext(self.cfg.get('file'))
        # dst_file = f"{base}_biba{ext}"
        # shutil.copy(self.cfg.get('file'), dst_file)

        # connection = sqlite3.connect(self.cfg.get('db_name'))
        # connection.row_factory = sqlite3.Row
        # cursor = connection.cursor()

        # table_name = self.table_name()
        # rows = cursor.execute(f"SELECT * FROM {table_name}").fetchall()
        # connection.close()

        # wb = load_workbook(dst_file)
        # sheet = wb.active

        # for row in rows:
        #     line_number = row['excel_line_number']
        #     for key in self.excel_map():
        #         value = self.excel_map()[key]
        #         sheet.cell(row=line_number, column=self.cfg.index(value) + 1, value=row[key])

        # wb.save(dst_file)
        print('Сохранено!')
