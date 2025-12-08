import sqlite3
from common.sqlite import safe_execute
from globals import Config
from office_sud_kz.generateFilesByTemplate.main import run as generatorRun
from flow_types.baseWithExcel import WithExcelType

class GenerateFilesByTemplateType(WithExcelType):
    def __init__(self, cfg: Config = None):
        self.__config_excel_keys_map = {
                key: {
                    'table_column': key.lower().replace('generatefiles_excel_key_', ''),
                    'variable_name': "{" + key.replace('generatefiles_excel_key_', '') + "}"
                    }
                for key in cfg.data.keys()
                if 'generatefiles_excel_key_' in key
        }
        super().__init__(cfg)

    @property
    def config_excel_keys_map(self):
        return self.__config_excel_keys_map

    def label(self)->str:
        return 'Генерация файлов по шаблону'

    def table_name(self)->str:
        return 'generate_files_by_template'

    def excel_map(self):
        return {
            'status': 'excel_status',
            'status_text': 'excel_status_text'
        }

    def migration(self):
        base_columns = [
            'id INTEGER PRIMARY KEY',
            'excel_line_number INTEGER',
            'status TEXT',
            'status_text TEXT',
            'generated_file_name TEXT'
        ]

        columns = list(self.config_excel_keys_map.values())
        columns = [value['table_column'] + ' TEXT' for value in self.config_excel_keys_map.values()]
        columns = base_columns + columns
        columns = ",".join(columns)

        connection = sqlite3.connect(self.cfg.get('db_name'))
        cursor = connection.cursor()

        cursor.execute(f'''
            DROP TABLE IF EXISTS {self.table_name()}
            ''')

        cursor.execute(f'''
            CREATE TABLE {self.table_name()}(
                    {columns}
                    )
                        ''')
        connection.commit()
        connection.close()

    def insert(self, row: tuple, cursor: sqlite3.Cursor, i):
        def safe_get(column_name: str) -> str:
            try:
                idx = self.cfg.index(column_name)
                return str(row[idx].value) if row[idx].value is not None else ""
            except (ValueError, IndexError):
                return ""

        data = {
            "status": safe_get('excel_status'),
            "status_text": safe_get('excel_status_text'),
            "generated_file_name": safe_get('generatefiles_excel_generated_file_name'),
            "excel_line_number": i,
        }

        for key, value in self.config_excel_keys_map.items():
            data[value['table_column']] = safe_get(key)

        columns = ", ".join(data.keys())
        placeholders = ", ".join([":" + key for key in data.keys()])
        query = f"INSERT INTO {self.table_name()}({columns}) VALUES ({placeholders})"

        cursor.execute(query, data)

    def _process_rows(self, ids, worker_id):
        print(f"[Worker {worker_id}] starting...")

        connection = sqlite3.connect(self.cfg.get('db_name'), timeout=30)
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA synchronous=NORMAL;")
        connection.execute("PRAGMA busy_timeout = 5000;")
        connection.row_factory = sqlite3.Row

        placeholder = ','.join('?' * len(ids))
        rows = connection.execute(f"SELECT * FROM {self.table_name()} WHERE id in ({placeholder})", ids).fetchall()

        for row in rows:
            excel_line_number = row['excel_line_number']
            print(f"[Worker {worker_id}] row: {excel_line_number} -> start")
            self.run(connection, row, worker_id)

        connection.commit()
        connection.close()

    def _get_data(self, row) -> dict | str:
        replace = {
            value['variable_name']: row[value['table_column']]
            for _, value in self.config_excel_keys_map.items()
        }

        data = {
            'replace': replace,
            'template_file_name': self.cfg.get('generatefiles_template_file_name'),
            'generated_file_name': row['generated_file_name'] + '.docx'
        }

        return data

    def run(self, connection, row, worker_id):
        data = self._get_data(row)

        try:
            generatorRun(data, worker_id)
            safe_execute(connection, f"UPDATE {self.table_name()} SET status = ?, status_text = ? WHERE id = ?", ('success', '', row['id']))
        except Exception as e:
            safe_execute(connection, f"UPDATE {self.table_name()} SET status = ?, status_text = ? WHERE id = ?", ('error', str(e), row['id']))
