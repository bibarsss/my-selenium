import sqlite3
from globals import Config

def label():
    return 'Иск проверка статуса'

def table_name():
    return 'iskstatus'

def excel_map():
    return {
        'status': 'excel_status',
        'status_text': 'excel_status_text' 
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
                    sud_name TEXT, 
                    result TEXT, 
                    status TEXT,
                    status_text TEXT                            
                   )
                        ''')
    connection.commit()        
    connection.close()

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

    columns = ", ".join(data.keys())
    placeholders = ", ".join([":" + key for key in data.keys()])
    query = f"INSERT INTO {table_name()}({columns}) VALUES ({placeholders})"

    cursor.execute(query, data)