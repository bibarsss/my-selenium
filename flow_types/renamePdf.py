# Cкачиванием файлов с ск Письмо
from datetime import datetime
from multiprocessing import Process
import os
from pathlib import Path
import re
import sqlite3
from common.read_pdf import read
from flow_types.baseWithoutExcel import WithoutExcelType

class RenamePdfType(WithoutExcelType):
    def label(self):
        return 'Переименование PDF файлов (Ринейм ИИН, ИН, Пост, ИЛ)'

    def table_name(self)->str:
        return 'rename_pdf'

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

    def insert(self, data, cursor: sqlite3.Cursor):
        columns = ", ".join(data.keys())
        placeholders = ", ".join([":" + key for key in data.keys()])
        query = f"INSERT INTO {self.table_name()}({columns}) VALUES ({placeholders})"
        cursor.execute(query, data)

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
        connection.close()

        print('Парсим файлы и переименовываем...')
        n_workers = 10
        # n_workers = 1
        chunks = self.chunk_list(ids, n_workers)
        rename_files = []
        for wid, chunk in enumerate(chunks):
            p = Process(target=self._parse_files, args=(chunk, wid))
            p.start()
            rename_files.append(p)
        for p in rename_files:
            p.join()

    def _parse_files(self, ids, worker_id):
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
            text = " ".join(text.splitlines())
            prefix = self.get_prefix(text)

            iin = self.extract_iin(text)
            if not iin:
                continue

            count = 0
            while True:
                new_name = f"{iin}"
                if count != 0:
                    new_name = f"{iin}-{count}"

                new_name = prefix + " - " + new_name + '.pdf'
                new_path = file_path.with_name(new_name)

                if new_path.exists():
                    count += 1
                    continue

                try:
                    file_path.rename(new_path)
                    print(f"[Worker {worker_id}] Renamed: {file_path.name} -> {new_path.name}")
                    break
                except Exception:
                    count += 1
                    continue

    def get_prefix(self, all_text):
        if 'постановление' in all_text.lower():
            return 'постановление'

        if 'исполнительный лист' in all_text.lower():
            return 'исполнительный_лист'

        if 'исполнительная надпись' in all_text.lower():
            return 'исполнительная_надпись'

        return ''

    def extract_iin(self, text):
        def is_probable_iin(num):
            try:
                datetime.strptime(num[:6], "%y%m%d")
                return True
            except ValueError:
                return False

        match = re.search(r'\([^)]+?(\d{12})\)', text)
        if match:
            candidate = match.group(1)
            if is_probable_iin(candidate):
                return candidate

        for num in re.findall(r'\b\d{12}\b', text):
            if is_probable_iin(num):
                return num
        return None
