# Cкачиванием файлов с ск Письмо
from multiprocessing import Process
import os
import sqlite3
import time

import requests
import urllib3
from common.sqlite import safe_execute
from flow_types.baseWithoutExcel import WithoutExcelType
from globals import RETRY_COUNT
from office_sud_kz.downloadIspListPismo.main import run as pismoRun

class DownloadIskListPismoType(WithoutExcelType):
    def label(self):
        return 'Cкачиванием файлов с ск Письмо'

    def table_name(self):
        return 'download_isp_list_pismo'

    def migration(self):
        connection = sqlite3.connect(self.cfg.get('db_name'))

        cursor = connection.cursor()
        cursor.execute(f'''
            DROP TABLE IF EXISTS {self.table_name()}
            ''')
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name()}(
                        id INTEGER PRIMARY KEY,
                        file_name TEXT,
                        url TEXT UNIQUE
                    )
                            ''')
        connection.commit()
        connection.close()

    def insert(self, data, connection):
        for i in data:
            tmp = {
                "file_name": i['file_name'],
                "url": i['url']
            }
            columns = ", ".join(tmp.keys())
            placeholders = ", ".join([":" + key for key in tmp.keys()])

            safe_execute(connection, f'''INSERT OR IGNORE INTO {self.table_name()}({columns}) VALUES ({placeholders})''', tmp)

    def start(self):
        def chunk_list(lst, n):
            k, m = divmod(len(lst), n)
            return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


        n_workers = int(self.cfg.get("count_process") or 1)
        flows = {
            1: "Запуск парсера + скачивание файлов",
            2: "Запуск скачивание файлов"
        }
        options = ",\n".join(f"{k} -> {v}" for k, v in flows.items())
        print('==========================')
        print(options)
        print('==========================')
        flow = int(input())

        if flow not in flows:
            print('Неправильный флоу')
            return

        if flow == 1:
            self.migration()
            processes = []
            for wid in range(n_workers):
                p = Process(target=self._process_pages, args=(wid, n_workers,))
                p.start()
                processes.append(p)

            for p in processes:
                p.join()

        print("Парсер: Получение ссылок для скачивание завершено!")
        print("Начинается скачивание...")

        connection = sqlite3.connect(self.cfg.get('db_name') )
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        ids = [r[0] for r in cursor.execute(f"SELECT id FROM {self.table_name()}")]
        connection.close()

        print(f"Найдено {len(ids)} файлов")

        n_workers = 20
        chunks = chunk_list(ids, n_workers)

        processes2 = []
        for wid, chunk in enumerate(chunks):
            p = Process(target=self._process_rows, args=(chunk, wid))
            p.start()
            processes2.append(p)

        for p in processes2:
            p.join()

        print("Скачивание завершено!")

    def _process_pages(self, worker_id, n_workers):
        from office_sud_kz.auth import auth
        print(f"[Worker {worker_id}] starting...")
        browser = self.browser()

        c = 0
        while not browser.htmlHasText('Редактировать профиль'):
            c += 1
            if c == RETRY_COUNT:
                raise Exception("Ошибка авторизации")
            browser.main_office_sud_kz()
            browser.wait_for_loader_done()
            auth(browser, self.cfg)
            browser.wait_for_loader_done()

        data = {
            "main_date_start":self.cfg.get('download_ispol_list_pismo_date_start'),
            "main_date_end":self.cfg.get('download_ispol_list_pismo_date_end'),
            "worker_id":worker_id,
            "n_workers":n_workers
        }

        try:
            pismoRun(browser, data, self)
        except Exception as e:
            print(e)
            print(f"[Worker {worker_id}] stopped...")

    def _process_rows(self, ids, worker_id):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        print(f"[Worker {worker_id}] starting...")

        connection = sqlite3.connect(self.cfg.get('db_name'), timeout=30)
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA synchronous=NORMAL;")
        connection.execute("PRAGMA busy_timeout = 5000;")
        connection.row_factory = sqlite3.Row

        placeholder = ','.join('?' * len(ids))
        rows = connection.execute(f"SELECT * FROM {self.table_name()} WHERE id in ({placeholder})", ids).fetchall()

        for row in rows:
            # print(f"[Worker {worker_id}] downloading - {row['file_name']}")
            c = 0
            while True:
                c += 1
                if c == RETRY_COUNT:
                    print(f"[Worker {worker_id}] - Couldn't download a file - {row['file_name']}. Link - [{row['url']}]")
                    break

                try:
                    self.run(row)
                    break
                except Exception as e:
                    time.sleep(1)

        connection.commit()
        connection.close()

    def run(self, row):
        folder = "pismo_downloads"
        os.makedirs(folder, exist_ok=True)

        output_file = os.path.join(folder, row['file_name'])

        response = requests.get(row['url'], verify=False)
        response.raise_for_status()

        with open(output_file, "wb") as f:
            f.write(response.content)
