# Cкачиванием файлов с ск Письмо
from datetime import datetime
from multiprocessing import Process
import os
from pathlib import Path
import re
import sqlite3
from common.read_pdf import read
from flow_types.baseWithoutExcel import WithoutExcelType

class DistributeIspListType(WithoutExcelType):
    def label(self):
        return 'Распределение испол листов по регионам'

    def table_name(self)->str:
        return 'distribute_isp_list'

    def migration(self):
        connection = sqlite3.connect(self.cfg.get('db_name'))

        cursor = connection.cursor()
        cursor.execute(f'''
            DROP TABLE IF EXISTS {self.table_name()}
            ''')

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name()}(
                        id INTEGER PRIMARY KEY,
                        file_path TEXT,
                        region TEXT
                    )
                            ''')
        connection.commit()
        connection.close()

    def start(self):
        self.migration()

        print('Ищем pdf...')
        connection = sqlite3.connect(self.cfg.get('db_name') )
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        for path in Path(".").glob("*.pdf"):
            self.insert({'file_path': str(path)}, cursor)

        connection.commit()
        ids = [r[0] for r in cursor.execute(f"SELECT id FROM {self.table_name()}")]

        print('Читаем файлы...')
        n_workers = 10
        chunks = self.chunk_list(ids, n_workers)
        parse_files = []
        for wid, chunk in enumerate(chunks):
            p = Process(target=self._parse_files, args=(chunk, wid))
            p.start()
            parse_files.append(p)
        for p in parse_files:
            p.join()

        ids = [r[0] for r in cursor.execute(f"SELECT id FROM {self.table_name()} WHERE region IS NOT NULL")]
        connection.close()

        print('Перемещаем файлы...')
        chunks = self.chunk_list(ids, n_workers)
        move_files = []
        for wid, chunk in enumerate(chunks):
            p = Process(target=self._move_files, args=(chunk, wid))
            p.start()
            move_files.append(p)
        for p in move_files:
            p.join()

    def _move_files(self, ids, worker_id):
        print(f"[Worker {worker_id}] starting...")
        folder_path = Path('распределение_испол_листов')
        os.makedirs(str(folder_path), exist_ok=True)

        connection = sqlite3.connect(self.cfg.get('db_name'), timeout=30)
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA synchronous=NORMAL;")
        connection.execute("PRAGMA busy_timeout = 5000;")
        connection.row_factory = sqlite3.Row

        placeholder = ','.join('?' * len(ids))
        rows = connection.execute(f"SELECT * FROM {self.table_name()} WHERE id in ({placeholder})", ids).fetchall()
        connection.close()

        for row in rows:
            region_path = folder_path / row['region']
            list_path = Path(row['file_path'])
            os.makedirs(str(region_path), exist_ok=True)
            if list_path.exists():
                list_target_path = region_path / row['file_path']
                os.replace(list_path, list_target_path)

    def _parse_files(self, ids, worker_id):
        print(f"[Worker {worker_id}] starting...")

        connection = sqlite3.connect(self.cfg.get('db_name'), timeout=30)
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA synchronous=NORMAL;")
        connection.execute("PRAGMA busy_timeout = 5000;")
        connection.row_factory = sqlite3.Row

        placeholder = ','.join('?' * len(ids))
        rows = connection.execute(f"SELECT * FROM {self.table_name()} WHERE id in ({placeholder})", ids).fetchall()

        for row in rows:
            file_path = Path(row['file_path'])

            text = read(os.path.abspath(str(file_path)))
            text = " ".join(text.splitlines())

            matches = re.findall(r"Фактический адрес:\s*[^,]+,\s*([^,]+),", text)
            if len(matches) >= 2:
                region = matches[1]
                self.update(row['id'], {'region': region}, connection)

        connection.commit()
        connection.close()
