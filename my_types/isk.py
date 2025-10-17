import sqlite3
from globals import Config
from pathlib import Path
import unicodedata

def excel_map():
    return {
        'status': 'excel_status',
        'status_text': 'excel_status_text' 
    }

def get_data(row, cfg: Config):
        number = row['number'] 

        dir = None
        for path in Path(".").rglob("*.pdf"):
            if number in unicodedata.normalize("NFC", path.name):
                dir = path.parent
                break

        if not dir:
            return 'Папка не найдена!' 
            
        data = {
            "iin": str(cfg.get('iin')).zfill(12),
            "bin": cfg.get('bin'),
            "phone": cfg.get('phone'),
            "address": cfg.get('address'),
            "detail": cfg.get('detail'),
            "number": number,
            "dir": str(dir),
            "phone_otvet4ik": row['phone_otvet4ik'],
            "podsudnost": row['podsudnost'],
            "iin_otvet4ik": str(row['iin_otvet4ik']).zfill(12),
            "summaIska": row['summaIska'],
            "powlina": row['powlina'],
            "powlina_file_path": str(dir / cfg.get('isk_powlina_file_name')),
            "isk_file_path": str(dir / cfg.get('isk_file_name')),
            "isk_file_realpath": str(dir / (str(cfg.get('isk_excel_file_name')) + ".pdf")),
        }
        return data 

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
                    iin_otvet4ik TEXT NOT NULL, 
                    number TEXT NOT NULL, 
                    phone_otvet4ik TEXT NOT NULL, 
                    podsudnost TEXT NOT NULL, 
                    summaIska TEXT NOT NULL, 
                    powlina TEXT NOT NULL, 
                    isk_file_realname TEXT NOT NULL,
                    status TEXT,
                    status_text TEXT                            
                   )
                        ''')
    connection.commit()        
    connection.close()

def label():
    return 'ИСК'

def table_name():
    return 'isk'

def insert(row: tuple, cfg: Config, cursor: sqlite3.Cursor, i):
    def safe_get(column_name: str) -> str:
        try:
            idx = cfg.index(column_name)
            return str(row[idx].value) if row[idx].value is not None else ""
        except (ValueError, IndexError):
            # ValueError if column name not found in config
            # IndexError if row doesn't have that many columns
            return ""

    data = {
        "number": safe_get('isk_excel_number'),
        "phone_otvet4ik": safe_get('isk_excel_phone_otvet4ik'),
        "podsudnost": safe_get('isk_excel_podsudnost'),
        "iin_otvet4ik": safe_get('isk_excel_iin_otvet4ik'),
        "summaIska": safe_get('isk_excel_summa_iska'),
        "powlina": safe_get('isk_excel_powlina'),
        "isk_file_realname": safe_get('isk_excel_file_name') + ".pdf",
        "status": safe_get('excel_status'),
        "status_text": safe_get('excel_status_text'),
        "excel_line_number": i,
    }

    # Validate that required fields are not None or 'None'
    if not all(v is not None and v != 'None' for k, v in data.items() if k not in ['status', 'status_text']):
        return

    columns = ", ".join(data.keys())
    placeholders = ", ".join([":" + key for key in data.keys()])
    query = f"INSERT INTO isk({columns}) VALUES ({placeholders})"

    cursor.execute(query, data)
