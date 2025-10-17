import sqlite3
from globals import Config

def label():
    return 'Иск проверка статуса'

def table_name():
    return 'iskstatus'


def migration(db: str):
    connection = sqlite3.connect(db)
    
    cursor = connection.cursor()
    cursor.execute('''
        DROP TABLE IF EXISTS isk 
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS isk(
                    id INTEGER PRIMARY KEY,
                    excel_line_number INTEGER,
                    number TEXT NOT NULL, 
                    sud_name TEXT, 
                    result TEXT, 
                    status TEXT,
                    status_text TEXT                            
                   )
                        ''')
    connection.commit()        
    connection.close()

def insert(row: tuple, cfg: Config, cursor: sqlite3.Cursor, i):
    data = {
        "talon": str(row[cfg.index('iskstatus_excel_talon')].value),
        "excel_line_number": i
        }

    columns = ", ".join(data.keys())
    placeholders = ", ".join([":" + key for key in data.keys()])
    query = f"INSERT INTO isk({columns}) VALUES ({placeholders})"

    cursor.execute(query, data)