# Cкачиванием файлов с ск Письмо
from multiprocessing import Process
from pathlib import Path
import sqlite3
import requests
from flow_types.baseWithoutExcel import WithoutExcelType

class ConverterType(WithoutExcelType):
    def label(self):
        return 'Конвертирование .docx на .pdf'

    def table_name(self)->str:
        return 'converter'

    def migration(self):
        connection = sqlite3.connect(self.cfg.get('db_name'))

        cursor = connection.cursor()
        cursor.execute(f'''
            DROP TABLE IF EXISTS {self.table_name()}
            ''')

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name()}(
                        id INTEGER PRIMARY KEY,
                        file_path TEXT
                    )
                            ''')
        connection.commit()
        connection.close()

    def start(self):
        self.migration()

        print('Ищем docx...')
        connection = sqlite3.connect(self.cfg.get('db_name') )
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        for path in Path(".").glob("*.doc*"):
            self.insert({'file_path': str(path)}, cursor)

        connection.commit()
        ids = [r[0] for r in cursor.execute(f"SELECT id FROM {self.table_name()}")]
        connection.close()

        print('Конвертируем...')
        n_workers = 5
        chunks = self.chunk_list(ids, n_workers)
        convert_files = []
        for wid, chunk in enumerate(chunks):
            p = Process(target=self._convert_files, args=(chunk, wid))
            p.start()
            convert_files.append(p)
        for p in convert_files:
            p.join()

    def _convert_files(self, ids, worker_id):
        print(f"[Worker {worker_id}] starting...")

        URL = "http://gotenberg.neocode.kz:3000/forms/libreoffice/convert"

        connection = sqlite3.connect(self.cfg.get('db_name'), timeout=30)
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA synchronous=NORMAL;")
        connection.execute("PRAGMA busy_timeout = 5000;")
        connection.row_factory = sqlite3.Row

        placeholder = ','.join('?' * len(ids))
        rows = connection.execute(f"SELECT * FROM {self.table_name()} WHERE id in ({placeholder})", ids).fetchall()

        connection.close()

        for row in rows:
            file_path = Path(row['file_path'])

            output_path = file_path.with_suffix('.pdf')
            print(f"[Worker {worker_id}] [{file_path.name}] converting...")

            with file_path.open('rb') as f:
                files = {'files': f}
                try:
                    response = requests.post(URL, files=files, timeout=30)
                    response.raise_for_status()
                    output_path.write_bytes(response.content)
                except Exception as e:
                    print(f"[Worker {worker_id}] Failed {file_path.name}: {e}")
