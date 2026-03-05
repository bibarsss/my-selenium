# Cкачиванием файлов с ск Письмо
from datetime import datetime
from multiprocessing import Process
import os
from pathlib import Path
import re
import sqlite3
from common.read_pdf import read
from common.sqlite import safe_execute
from flow_types.baseWithoutExcel import WithoutExcelType
import shutil

class RenamePdfType(WithoutExcelType):
    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = value

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
                        file_path TEXT,
                        file_name TEXT,
                        number TEXT,
                        iin TEXT
                    )
                            ''')
        connection.commit()
        connection.close()

    def start(self):
        types = {
            1: 'Ренейм ИИН, ИН, Пост, ИЛ (иин)',
            2: 'Решение для аисоип (фио)',
            3: 'Ренейм определение (исп листы должны иметь в названии слово "лист")'
        }
        options = ".\n".join(f"{k} -> {v}" for k, v in types.items())
        try:
            print('==========================')
            print(options)
            print('==========================')

            self.type = int(input(f"Введите тип флоу: "))
            if self.type not in types.keys():
                print("Неправильный тип флоу: ", self.type)
                return
        except Exception as e:
            print("Неправильный тип флоу!")
            return

        self.migration()

        print('Ищем pdf...')
        connection = sqlite3.connect(self.cfg.get('db_name') )
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        for path in Path(".").glob("*.pdf"):
            self.insert({
                'file_path': str(path),
                'file_name': path.name
                }, cursor)

        connection.commit()
        connection.close()

        if self.type == 1:
            self.rename_to_iin()
        elif self.type == 2:
            self.rename_to_fio_aisoip()
        elif self.type == 3:
            self.rename_to_iin_definition()

    def rename_to_iin(self):
        connection = sqlite3.connect(self.cfg.get('db_name') )
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        ids = [r[0] for r in cursor.execute(f"SELECT id FROM {self.table_name()}")]
        connection.close()

        print('Парсим файлы и переименовываем...')
        n_workers = 5
        chunks = self.chunk_list(ids, n_workers)
        rename_files = []
        for wid, chunk in enumerate(chunks):
            p = Process(target=self.to_iin, args=(chunk, wid))
            p.start()
            rename_files.append(p)
        for p in rename_files:
            p.join()

    def to_iin(self, ids, worker_id):
        def get_prefix(all_text):
            all_text = all_text.lower()

            if 'постановление' in all_text:
                if 'нотариус' in all_text:
                    return 'постановление_об_отмене_исп_надписи'
                return 'постановление'

            if 'исполнительный лист' in all_text:
                if 'полное наименование взыскателя и его адрес' in all_text:
                    return 'исп_лист'

                if 'определение' in all_text:
                    return 'определение'

            if 'исполнительная надпись' in all_text:
                return 'исп_надпись'

            return ''

        def extract_iin(text):
            black_list = ['020116601379']
            def is_probable_iin(num):
                try:
                    datetime.strptime(num[:6], "%y%m%d")
                    return True
                except ValueError:
                    return False

            # match = re.search(r'\([^)]+?(\d{12})\)', text)
            # if match:
            #     candidate = match.group(1)
            #     if is_probable_iin(candidate):
            #         return candidate

            for num in re.findall(r'\b\d{12}\b', text):
                if num in black_list:
                    continue

                if is_probable_iin(num):
                    return num

            return None

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
            try:
                file_path = Path(row['file_path'])
                text = read(os.path.abspath(str(file_path)))
                text = " ".join(text.splitlines())

                prefix = get_prefix(text)

                iin = extract_iin(text)
                if not iin:
                    continue

                count = 0
                while True:
                    suffix = f"-{count}" if count else ""
                    name = f"{iin}{suffix}.pdf"

                    if prefix:
                        name = f"{prefix} - {name}"

                    new_path = file_path.with_name(name)

                    try:
                        file_path.rename(new_path)
                        print(f"[Worker {worker_id}] Renamed: {file_path.name} -> {new_path.name}")
                        break

                    except FileExistsError:
                        count += 1
                        continue

            except Exception as e:
                print(f"[Worker {worker_id}] Couldn't read pdf file: [{Path(row['file_path'])}]")
                continue

    def rename_to_fio_aisoip(self):
        connection = sqlite3.connect(self.cfg.get('db_name') )
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        ids = [r[0] for r in cursor.execute(f"SELECT id FROM {self.table_name()}")]
        connection.close()

        print('Парсим файлы и переименовываем...')
        n_workers = 5
        chunks = self.chunk_list(ids, n_workers)
        rename_files = []
        for wid, chunk in enumerate(chunks):
            p = Process(target=self.to_fio_aisoip, args=(chunk, wid))
            p.start()
            rename_files.append(p)
        for p in rename_files:
            p.join()

    def to_fio_aisoip(self, ids, worker_id):
        def extract_fio(text: str) -> list[str]:
            pattern = r'ОТВЕТЧИКИ?:\s*(.+?)\s*ТРЕБОВАНИЯ\s+ИСТЦА:'
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

            if not match:
                return []

            block = match.group(1).strip()
            lines = re.split(r'[\n\r]+', block)

            result = [line.strip() for line in lines if line.strip()]

            return result

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
            try:
                file_path = Path(row['file_path'])
                text = read(os.path.abspath(str(file_path)))
                # text = " ".join(text.splitlines())

                if 'р е ш е н и е' not in text.lower() and 'решение' not in text.lower():
                    continue

                fios = extract_fio(text)
                copied_any = False

                for fio in fios:
                    prefix = 'Решение'
                    count = 0

                    while True:
                        suffix = f"-{count}" if count else ""
                        name = f"{fio}{suffix}.pdf"

                        if prefix:
                            name = f"{prefix} - {name}"

                        new_path = file_path.with_name(name)

                        try:
                            shutil.copy2(file_path, new_path)
                            print(f"[Worker {worker_id}] Copied: {file_path.name} -> {new_path.name}")
                            copied_any = True
                            break

                        except FileExistsError:
                            count += 1
                            continue

                if copied_any:
                    try:
                        file_path.unlink()
                    except Exception as e:
                        pass

            except Exception as e:
                print(f"[Worker {worker_id}] Couldn't read pdf file: [{Path(row['file_path'])}]")
                continue

    def rename_to_iin_definition(self):
        connection = sqlite3.connect(self.cfg.get('db_name') )
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        search_text = 'лист'
        ids = [
            r[0]
            for r in cursor.execute(
                f"SELECT id FROM {self.table_name()} WHERE LOWER(file_name) LIKE LOWER(?)",
                (f"%{search_text}%",)
            )
        ]
        connection.close()

        print('Парсим только листы и сохраняем...')
        n_workers = 5
        chunks = self.chunk_list(ids, n_workers)
        rename_files = []
        for wid, chunk in enumerate(chunks):
            p = Process(target=self.to_iin_definition_parse, args=(chunk, wid))
            p.start()
            rename_files.append(p)
        for p in rename_files:
            p.join()

        connection = sqlite3.connect(self.cfg.get('db_name') )
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        ids = [
            r[0]
            for r in cursor.execute(
                f"SELECT id FROM {self.table_name()} WHERE LOWER(file_name) NOT LIKE LOWER(?)",
                (f"%{search_text}%",)
            )
        ]
        connection.close()

        print('Переименовываем...')
        n_workers = 5
        chunks = self.chunk_list(ids, n_workers)
        rename_files = []
        for wid, chunk in enumerate(chunks):
            p = Process(target=self.to_iin_definition, args=(chunk, wid))
            p.start()
            rename_files.append(p)
        for p in rename_files:
            p.join()

    def to_iin_definition_parse(self, ids, worker_id):
        def parse_list(text: str):
            result = {}

            # -------------------------
            # ИИН (12 цифр)
            # -------------------------
            iin_match = re.search(r'ИИН[:\s]+(\d{12})', text)
            result['iin_client'] = iin_match.group(1) if iin_match else None

            # -------------------------
            # Номер дела
            # -------------------------
            number_match = re.search(r'№\s*([\d\-\/]+)', text)
            result['number'] = number_match.group(1) if number_match else None

            missing_fields = [k for k, v in result.items() if v is None]
            if missing_fields:
                return None

            return result

        print(f"[Worker {worker_id}] starting...")

        connection = sqlite3.connect(self.cfg.get('db_name'), timeout=30)
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA synchronous=NORMAL;")
        connection.execute("PRAGMA busy_timeout = 5000;")
        connection.row_factory = sqlite3.Row

        placeholder = ','.join('?' * len(ids))
        rows = connection.execute(f"SELECT * FROM {self.table_name()} WHERE id in ({placeholder})", ids).fetchall()

        for row in rows:
            try:
                file_path = Path(row['file_path'])
                text = read(os.path.abspath(str(file_path)))
                parsed_data = parse_list(text)
                if not parsed_data:
                    continue

                safe_execute(connection, f'''UPDATE {self.table_name()}
                            SET number = ?,
                            iin = ?
                            WHERE id = ?
                            ''',
                            (parsed_data['number'],
                            parsed_data['iin_client'],
                            row['id']),)

            except Exception as e:
                print(f"[Worker {worker_id}] Couldn't read pdf file: [{Path(row['file_path'])}]")
                continue

        connection.close()

    def to_iin_definition(self, ids, worker_id):
        def parse_file_for_number(text: str):
            result = {}

            # -------------------------
            # Номер дела
            # -------------------------
            number_match = re.search(r'№\s*([\d\-\/]+)', text)
            result['number'] = number_match.group(1) if number_match else None

            missing_fields = [k for k, v in result.items() if v is None]
            if missing_fields:
                return None

            return result

        print(f"[Worker {worker_id}] starting...")

        connection = sqlite3.connect(self.cfg.get('db_name'), timeout=30)
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA synchronous=NORMAL;")
        connection.execute("PRAGMA busy_timeout = 5000;")
        connection.row_factory = sqlite3.Row

        placeholder = ','.join('?' * len(ids))
        rows = connection.execute(f"SELECT * FROM {self.table_name()} WHERE id in ({placeholder})", ids).fetchall()

        for row in rows:
            try:
                file_path = Path(row['file_path'])
                text = read(os.path.abspath(str(file_path))).lower()
                if 'определение' not in text and 'о п р е д е л е н и е' not in text:
                    continue

                parsed_data = parse_file_for_number(text)
                if not parsed_data:
                    continue

                one_row = connection.execute(
                    f"SELECT * FROM {self.table_name()} WHERE number LIKE ? AND iin IS NOT NULL",
                    (f"%{parsed_data['number']}%",)
                ).fetchone()
                if not one_row:
                    continue

                iin = one_row['iin']
                prefix = 'определение'

                count = 0
                while True:
                    suffix = f"-{count}" if count else ""
                    name = f"{iin}{suffix}.pdf"

                    if prefix:
                        name = f"{prefix} - {name}"

                    new_path = file_path.with_name(name)

                    try:
                        file_path.rename(new_path)
                        print(f"[Worker {worker_id}] Renamed: {file_path.name} -> {new_path.name}")
                        break

                    except FileExistsError:
                        count += 1
                        continue

            except Exception as e:
                print(f"[Worker {worker_id}] Couldn't read pdf file: [{Path(row['file_path'])}]")
                continue

        connection.close()
