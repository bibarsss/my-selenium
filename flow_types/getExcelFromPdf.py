# Cкачиванием файлов с ск Письмо
from datetime import datetime
from multiprocessing import Process
import os
from pathlib import Path
import re
import sqlite3

import pandas as pd
from common.read_pdf import read
from flow_types.baseWithoutExcel import WithoutExcelType

class GetExcelFromPdfType(WithoutExcelType):
    def label(self):
        return 'Положить ФИО, ИИН, номер договора в эксель файл'

    def table_name(self)->str:
        return 'get_excel_from_pdf'

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
                        iin TEXT,
                        number TEXT,
                        full_name TEXT
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

        print('Парсим файлы...')
        n_workers = 10
        chunks = self.chunk_list(ids, n_workers)
        parse_files = []
        for wid, chunk in enumerate(chunks):
            p = Process(target=self._parse_files, args=(chunk, wid))
            p.start()
            parse_files.append(p)
        for p in parse_files:
            p.join()

        print('Сохраняем в эксель...')
        rows = connection.execute(f"""
                                  SELECT iin, number, full_name, file_path
                                  FROM {self.table_name()}
                                    """).fetchall()
        connection.close()

        columns = ["ИИН", "Номер договора", "ФИО", "Путь к файлу"]
        output_path = "output.xlsx"

        df = pd.DataFrame(rows, columns=columns)
        df.to_excel(output_path, index=False)

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
            iin = self.extract_iin(text)
            number = self.extract_agreement_number(text)
            full_name = self.extract_full_name(text)
            self.update(row_id=row['id'], data={
                'iin':iin,
                'number':number,
                'full_name':full_name
            }, connection=connection)

        connection.commit()
        connection.close()

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

    def extract_agreement_number(self, text: str):
        if not text:
            return None
        base_pattern = r"(?<![A-Za-z0-9])([ZL][0-9A-Z]{12,15}(?:-\d{1,2})?)\b"

        flags = re.IGNORECASE | re.DOTALL

        pattern_after_dogovor = rf"по\s*договору\s*{base_pattern}"
        m = re.search(pattern_after_dogovor, text, flags)
        if m:
            return m.group(1)

        for cand in re.findall(base_pattern, text, flags):
            if cand.upper().startswith("KZ"):
                continue
            if len(cand) > 17:  # safety threshold
                continue
            return cand

        return None

    def extract_full_name(self, text):
        match = re.search(r"взыскать по настоящему документу с\s+([А-ЯЁӘІҢҒҮҰҚӨа-яёәіңғүұқө\s]+?),", text, re.IGNORECASE)
        return match.group(1).strip() if match else None
