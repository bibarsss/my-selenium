#Проверка иск статуса
import sqlite3
from common.sqlite import safe_execute
from globals import Config
from office_sud_kz.iskstatus.main import run as iskstatusRun

def label():
    return 'Иск проверка статуса'

def table_name():
    return 'iskstatus'

def excel_map():
    return {
        'status': 'excel_status',
        'status_text': 'excel_status_text',
        'result': 'iskstatus_excel_result', 
        'result_date': 'iskstatus_excel_result_date', 
        'result_sud_name': 'iskstatus_excel_result_sud_name', 
        'result_number': 'iskstatus_excel_result_number', 
    }

def migration(db: str):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute(f'''
        DROP TABLE IF EXISTS {table_name()} 
        ''')
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name()}(
                    id INTEGER PRIMARY KEY,
                    excel_line_number INTEGER,
                    talon TEXT NOT NULL, 
                    result TEXT, 
                    result_date TEXT,
                    result_sud_name TEXT, 
                    result_number TEXT,
                    status TEXT,
                    status_text TEXT                            
                   )
                        ''')
    connection.commit()        
    connection.close()

def get_data(row, cfg: Config):
        data = {
            "talon": row['talon'],
        }
        return data 

def insert(row: tuple, cfg: Config, cursor: sqlite3.Cursor, i):
    def safe_get(column_name: str) -> str:
        try:
            idx = cfg.index(column_name)
            return str(row[idx].value) if row[idx].value is not None else ""
        except (ValueError, IndexError):
            return ""

    data = {
        "talon": str(row[cfg.index('iskstatus_excel_talon')].value),
        "excel_line_number": i,
        "status": safe_get('excel_status'),
        "status_text": safe_get('excel_status_text'),
        }
    
    talon = str(data.get('talon', '')).strip()  

    if not talon.isdigit():
        return

    columns = ", ".join(data.keys())
    placeholders = ", ".join([":" + key for key in data.keys()])
    query = f"INSERT INTO {table_name()}({columns}) VALUES ({placeholders})"

    cursor.execute(query, data)

def run(browser, data, connection, row, worker_id):
    try:
        parsed_data = iskstatusRun(browser, data, worker_id)
        # parsed_data = {
        #         'result': 'res',
        #         'result_date': 'result_date',
        #         'result_sud_name': 'result_sud_name',
        #         'result_number':'result_number' 
        # }
        safe_execute(connection, f'''UPDATE {table_name()} 
                     SET status = ?, 
                     status_text = ?, 
                     result = ?,
                     result_date = ?,
                     result_sud_name = ?,
                     result_number = ?
                     WHERE id = ?
                     ''', 
                     ('success', 
                      '', 
                      parsed_data['result'],
                      parsed_data['result_date'],
                      parsed_data['result_sud_name'],
                      parsed_data['result_number'],
                      row['id']),)
    except Exception as e:
        safe_execute(connection, f"UPDATE {table_name()} SET status = ?, status_text = ? WHERE id = ?", ('error', str(e), row['id']))