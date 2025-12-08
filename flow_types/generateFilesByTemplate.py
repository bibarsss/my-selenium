from pathlib import Path
import unicodedata
import sqlite3
from common.sqlite import safe_execute
from office_sud_kz.isk.main import run as iskRun
from flow_types.baseWithExcel import WithExcelType

class GenerateFilesByTemplateType(WithExcelType):
    def label(self)->str:
        return 'Генерация файлов по шаблону'

    def table_name(self)->str:
        return 'generate_files_by_template'

    def excel_map(self):
        return {}

    def migration(self):
        print('migration')
        connection = sqlite3.connect(self.cfg.get('db_name'))

        cursor = connection.cursor()

        cursor.execute(f'''
            DROP TABLE IF EXISTS {self.table_name()}
            ''')

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name()}(
                        id INTEGER PRIMARY KEY,
                        excel_line_number INTEGER,
                        status TEXT,
                        status_text TEXT
                    )
                            ''')
        connection.commit()
        connection.close()

    def insert(self, row: tuple, cursor: sqlite3.Cursor, i):
        return
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
        return {}
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
            "bin": self.cfg.get('bin'),
            "phone": self.cfg.get('phone'),
            "address": self.cfg.get('address'),
            "detail": self.cfg.get('detail'),
            "number": number,
            "dir": str(dir),
            "phone_otvet4ik": row['phone_otvet4ik'],
            "podsudnost": row['podsudnost'],
            "iin_otvet4ik": str(row['iin_otvet4ik']).zfill(12),
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

    def start(self):
        self.migration()

        wb = load_workbook(self.cfg.get('file'))
        sheet = wb.active
        rows = list(enumerate(sheet.iter_rows(min_row=2, values_only=False), start=2))

        connection = sqlite3.connect(self.cfg.get('db_name') )
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        for i, row in rows:
            self.insert(row, cursor, i)

        connection.commit()

        ids = [r[0] for r in cursor.execute(f"SELECT id FROM {self.table_name()} WHERE status != ?", ('success',))]
        connection.close()

        n_workers = int(self.cfg.get("count_process") or 1)
        chunks = chunk_list(ids, n_workers)

        processes = []
        for wid, chunk in enumerate(chunks):
            p = Process(target=self._process_rows, args=(chunk, wid))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        self.save_to_excel()
