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

    def start(self):
        print('Смотрим папки и подпапки...')
        self.migration()

#Get paths to blank.pdf file
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

#Parse blank.pdf files
        print('Парсим файлы...')
        n_workers = 10
        chunks = self.chunk_list(ids, n_workers)
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
        ids = [r[0] for r in cursor.execute(f"SELECT id FROM {self.table_name()} WHERE talon IS NOT NULL AND talon <> ''")]
        connection.close()

#Move talon files to the blank.pdf paths
        print('Перемещаем файлы...')
        chunks = self.chunk_list(ids, n_workers)
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

        placeholders_talon = ",".join(["?"] * len(pdf_file_names))
        placeholders_ids = ",".join(["?"] * len(ids))
        query = f"""
                SELECT *
                FROM {self.table_name()}
                WHERE talon IN ({placeholders_talon})
                AND id IN ({placeholders_ids})
            """
        params = pdf_file_names + ids
        rows = connection.execute(query, params).fetchall()
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

            try:
                text = read(os.path.abspath(blank_path))
            except Exception as e:
                print(f"[Worker {worker_id}] Talon ERROR! [{str(blank_path)}]")
                print(e)
                continue
            match = re.search(r"Құжат нөмірі \(номер документа\):\s*(\d+)", text)

            if not match:
                print(f"[Worker {worker_id}] Talon number not Found! [{str(blank_path)}]")
                continue
            doc_number = match.group(1)

            self.update(row['id'], {'talon': doc_number}, connection)

        connection.commit()
        connection.close()
