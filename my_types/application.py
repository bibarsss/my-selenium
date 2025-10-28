#Хотадайство
import sqlite3
from common.sqlite import safe_execute
from globals import Config
from office_sud_kz.application.main import run as applicationRun
from pathlib import Path 
import unicodedata


def label():
    return 'Хотадайство'

def table_name():
    return 'application'

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
                    iin TEXT,
                    podsudnost TEXT, 
                    nomer_dela TEXT, 
                    otvet4ik_po_delu TEXT, 
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
        "excel_line_number": i,
        'iin': str(row[cfg.index('application_excel_iin')].value),
        'podsudnost': str(row[cfg.index('application_excel_podsudnost')].value),
        'nomer_dela': str(row[cfg.index('application_excel_nomer_dela')].value),
        'otvet4ik_po_delu': str(row[cfg.index('application_excel_otvet4ik_po_delu')].value),
        "status": safe_get('excel_status'),
        "status_text": safe_get('excel_status_text'),
        }
    
    columns = ", ".join(data.keys())
    placeholders = ", ".join([":" + key for key in data.keys()])
    query = f"INSERT INTO {table_name()}({columns}) VALUES ({placeholders})"

    cursor.execute(query, data)

def get_data(row, cfg: Config):
        iin = str(row['iin']).zfill(12)

        dir = None
        file_name = None
        for path in Path(".").rglob("*.pdf"):
            if iin in unicodedata.normalize("NFC", path.name):
                dir = path.parent
                file_name = path.name
                break

        if not dir or not file_name:
            return f'Папка или файл не найден!' 

        data = {
            "iin": iin,
            "podsudnost": row['podsudnost'],
            "nomer_dela": row['nomer_dela'],
            "otvet4ik_po_delu": row['otvet4ik_po_delu'],
            "address": cfg.get('address'),
            'istcy_po_delu': cfg.get('application_istcy_po_delu'),
            'dir': dir,
            "file_path": str(dir / file_name),
        }

        return data 

def run(browser, data, connection, row, worker_id):
    if type(data) is str:
        safe_execute(connection, f"UPDATE {table_name()} SET status = ?, status_text = ? WHERE id = ?", ('skipped', data, row['id']))
        print(f"[Worker {worker_id}] row: {row['excel_line_number']} -> skipped")
        return 

    try:
        applicationRun(browser, data, worker_id)
        safe_execute(connection, f'''UPDATE {table_name()} 
                     SET status = ?, 
                     status_text = ? 
                     WHERE id = ?
                     ''', 
                     ('success', 
                      '', 
                      row['id']),)
    except Exception as e:
        safe_execute(connection, f'''UPDATE {table_name()} 
                     SET status = ?, 
                     status_text = ? 
                     WHERE id = ?''', 
                     ('error', str(e), row['id']),)

def excel_map():
    return {
        'status': 'excel_status',
        'status_text': 'excel_status_text',
    }