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

class GetExcelFromTalonPdfType(WithoutExcelType):
    def label(self):
        return 'Положить номер талона и дату в эксель'

    def table_name(self)->str:
        return 'get_excel_from_talon_pdf'

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
                        talon TEXT,
                        date TEXT
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
        for path in Path(".").rglob("*.pdf"):
            self.insert({'file_path': str(path)}, cursor)

        connection.commit()
        ids = [r[0] for r in cursor.execute(f"SELECT id FROM {self.table_name()}")]

        print('Парсим файлы...')
        # n_workers = 10
        n_workers = 1
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
                                  SELECT talon, date, file_path
                                  FROM {self.table_name()}
                                    """).fetchall()
        connection.close()

        columns = ["ТАЛОН", "ДАТА", "Путь к файлу"]
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
            text = " ".join(text.splitlines()).lower()
            if 'уведомление об отправке искового заявления через судебный кабинет уникальный номер' not in text \
                and 'талап арызды сот кабинеті арқылы жіберу туралы хабарлама' not in text:
                self.delete(row['id'], connection)
                continue

            date, number = self.extract_info(text)
            if not date or not number:
                self.delete(row['id'], connection)
                continue

            self.update(row_id=row['id'], data={
                'talon':number,
                'date':date
            }, connection=connection)

        connection.commit()
        connection.close()

    def extract_info(self, text):
        date_pattern = r"(дата отправки|жіберу күні):\s*([0-9]{2}\.[0-9]{2}\.[0-9]{4})"
        number_pattern = r"(уникальный номер|бірегей нөмір):\s*(\d+)"

        date_match = re.search(date_pattern, text)
        number_match = re.search(number_pattern, text)

        date = date_match.group(2) if date_match else None
        number = number_match.group(2) if number_match else None

        return date, number
