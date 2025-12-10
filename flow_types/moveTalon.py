# Cкачиванием файлов с ск Письмо
from multiprocessing import Process
import os
from pathlib import Path
import re
import sqlite3
from common.read_pdf import read
from common.sqlite import safe_execute
from flow_types.baseWithoutExcel import WithoutExcelType

class MoveTalonType(WithoutExcelType):
    def label(self):
        return 'Перемещение талонов по папкам где лежат blank.pdf файлы'

    def table_name(self)->str:
        return 'move_talon'

    def migration(self):
        connection = sqlite3.connect(self.cfg.get('db_name'))

        cursor = connection.cursor()
        cursor.execute(f'''
            DROP TABLE IF EXISTS {self.table_name()}
            ''')

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name()}(
                        id INTEGER PRIMARY KEY,
                        folder_path TEXT,
                        talon TEXT
                    )
                            ''')
        connection.commit()
        connection.close()

    def insert(self, data, cursor: sqlite3.Cursor):
        columns = ", ".join(data.keys())
        placeholders = ", ".join([":" + key for key in data.keys()])
        query = f"INSERT INTO {self.table_name()}({columns}) VALUES ({placeholders})"
        cursor.execute(query, data)

    def update(self, row_id, data, connection):
        set_clause = ", ".join([f"{key} = :{key}" for key in data.keys()])

        query = f"UPDATE {self.table_name()} SET {set_clause} WHERE id = :id"

        params = data.copy()
        params["id"] = row_id

        safe_execute(connection, query, params)

    def start(self):
        print('Смотрим папки и подпапки...')
        self.migration()

        connection = sqlite3.connect(self.cfg.get('db_name') )
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        root = Path('.')
        skip_folder = root / self.cfg.get('movetalon_folder_name')

        for folder in root.rglob("*"):
            if skip_folder in folder.parents or folder == skip_folder:
                continue

            if folder.is_dir() and (folder / "blank.pdf").exists():
                self.insert({'folder_path': str(folder)}, cursor)

        connection.commit()
        ids = [r[0] for r in cursor.execute(f"SELECT id FROM {self.table_name()}")]
        connection.close()

        n_workers = 10
        chunks = self.chunk_list(ids, n_workers)

        print('Парсим файлы...')
        parse_files_processes = []
        for wid, chunk in enumerate(chunks):
            p = Process(target=self._parse_files, args=(chunk, wid))
            p.start()
            parse_files_processes.append(p)

        for p in parse_files_processes:
            p.join()


        connection = sqlite3.connect(self.cfg.get('db_name') )
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        ids = [r[0] for r in cursor.execute(f"SELECT id FROM {self.table_name()} WHERE talon IS NOT NULL")]
        print(ids)
        connection.close()

        chunks = self.chunk_list(ids, n_workers)

        print('Перемещаем файлы...')
        move_files_processes = []
        for wid, chunk in enumerate(chunks):
            p = Process(target=self._move_files, args=(chunk, wid))
            p.start()
            move_files_processes.append(p)

        for p in move_files_processes:
            p.join()

    def _move_files(self, ids, worker_id):
        print(f"[Worker {worker_id}] starting...")
        folder_path = Path(self.cfg.get('movetalon_folder_name'))

        pdf_file_names = [f.name.replace('.pdf', '') for f in folder_path.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"]

        connection = sqlite3.connect(self.cfg.get('db_name'), timeout=30)
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA synchronous=NORMAL;")
        connection.execute("PRAGMA busy_timeout = 5000;")
        connection.row_factory = sqlite3.Row

        placeholders = ",".join(["?"] * len(pdf_file_names))
        query = f"SELECT * FROM {self.table_name()} WHERE talon IN ({placeholders})"

        rows = connection.execute(query, pdf_file_names).fetchall()
        connection.close()

        for row in rows:
            talon_file = folder_path / f"{row['talon']}.pdf"
            target_folder = Path(row['folder_path'])

            if talon_file.exists():
                target_file = target_folder / talon_file.name
                os.replace(talon_file, target_file)

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
            folder_path = Path(row['folder_path'])
            blank_path = folder_path / 'blank.pdf'

            if not blank_path.exists():
                print(f"[Worker {worker_id}] blank.pdf not Found! [{str(blank_path)}]")
                continue

            text = read(os.path.abspath(blank_path))
            match = re.search(r"Құжат нөмірі \(номер документа\):\s*(\d+)", text)

            if not match:
                print(f"[Worker {worker_id}] Talon number not Found! [{str(blank_path)}]")
                continue
            doc_number = match.group(1)  # only the number

            self.update(row['id'], {'talon': doc_number}, connection)

        connection.commit()
        connection.close()
