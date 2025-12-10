# Cкачиванием файлов с ск Письмо
from multiprocessing import Process
import os
from pathlib import Path
import sqlite3
import unicodedata
from common.read_pdf import read
from flow_types.baseWithoutExcel import WithoutExcelType

class RenameIskType(WithoutExcelType):
    def label(self):
        return 'Переименование ИСК'

    def table_name(self)->str:
        return 'rename_isk'

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

        print('Ищем иски...')
        connection = sqlite3.connect(self.cfg.get('db_name') )
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        for path in Path(".").rglob("*.pdf"):
            filename = unicodedata.normalize("NFC", path.name).lower()
            if "суд" in filename:
                self.insert({'file_path': str(path)}, cursor)

        connection.commit()
        ids = [r[0] for r in cursor.execute(f"SELECT id FROM {self.table_name()}")]
        connection.close()

        print('Парсим файлы и переименовываем...')
        n_workers = 10
        chunks = self.chunk_list(ids, n_workers)
        rename_files = []
        for wid, chunk in enumerate(chunks):
            p = Process(target=self._rename_files, args=(chunk, wid))
            p.start()
            rename_files.append(p)
        for p in rename_files:
            p.join()

    def _rename_files(self, ids, worker_id):
        print(f"[Worker {worker_id}] starting...")
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

            text = read(os.path.abspath(str(file_path)))
            if "исковое заявление" in text.lower():
                try:
                    new_path = file_path.with_name("Иск (1).pdf")
                    file_path.rename(new_path)
                    print(f"[Worker {worker_id}] Renamed: {file_path.name} -> {new_path.name}")
                except Exception:
                    print(f"[ERROR]: {file_path.name} -> {new_path.name}")
                    continue

