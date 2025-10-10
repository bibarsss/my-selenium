import sqlite3
from globals import Config
from pathlib import Path
import unicodedata
def get_data(row, cfg: Config):
        number = row['number'] 

        dir = None
        for path in Path(".").rglob("*.pdf"):
            if number in unicodedata.normalize("NFC", path.name):
                dir = path.parent
                break

        if not dir:
            return None
            
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
                    excel_line INTEGER,
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
    data = {
        "number": str(row[cfg.index('isk_excel_number')].value),
        "phone_otvet4ik": str(row[cfg.index('isk_excel_phone_otvet4ik')].value),
        "podsudnost": str(row[cfg.index('isk_excel_podsudnost')].value),
        "iin_otvet4ik": str(row[cfg.index('isk_excel_iin_otvet4ik')].value),
        "summaIska": str(row[cfg.index('isk_excel_summa_iska')].value),
        "powlina": str(row[cfg.index('isk_excel_powlina')].value),
        "isk_file_realname": str(row[cfg.index('isk_excel_file_name')].value) + ".pdf",
        "status": str(row[cfg.index('excel_status')].value),
        "status_text": str(row[cfg.index('excel_status_text')].value),
        "excel_line": i
        }

    if not all(v is not None and v != 'None' for k, v in data.items() if k not in ['status', 'status_text']):
        return

    columns = ", ".join(data.keys())
    placeholders = ", ".join([":" + key for key in data.keys()])
    query = f"INSERT INTO isk({columns}) VALUES ({placeholders})"

    cursor.execute(query, data)
    # globals.globalData = {
    #     "iin": globals.cfg['iin'],
    #     "bin": globals.cfg['bin'],
    #     "phone": globals.cfg['phone'],
    #     "phone_otvet4ik": "isk_excel_phone_otvet4ik"
    #     "address": globals.cfg['address'],
    #     "detail": globals.cfg['detail'],
    #     "podsudnost": str(row[globals.index('isk_excel_podsudnost')].value),
    #     "number": number,
    #     "iin_otvet4ik": str(row[globals.index('isk_excel_iin_otvet4ik')].value).zfill(12),
    #     "summaIska": str(row[globals.index('isk_excel_summa_iska')].value),
    #     "powlina": str(row[globals.index('isk_excel_powlina')].value),
    #     "dir": str(dir),
    #     "powlina_file_path": str(dir / globals.cfg['isk_powlina_file_name']),
    #     "isk_file_path": str(dir / globals.cfg['isk_file_name']),
    #     "isk_file_realpath": str(dir / (str(row[globals.index('isk_excel_file_name')].value) + ".pdf")),
    # }

# a = 'database_sud.db'

# run(a)

