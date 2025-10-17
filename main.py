import multiprocessing
from multiprocessing import Process
from pathlib import Path
from openpyxl import load_workbook
import globals
from my_types import isk as iskType
from my_types import status as statusType
import sqlite3
import os
import shutil
import time

types = {
        1: iskType,
        2: statusType
    }
    
def safe_execute(conn, query, params=(), retries=60):
    for i in range(retries):
        try:
            conn.execute(query, params)
            conn.commit()  # ✅ commit inside
            return
        except sqlite3.OperationalError as e:
            if "locked" in str(e):
                print(f"DB is locked, retrying in 0.5s... ({i+1}/{retries})")
                time.sleep(0.5)
            else:
                raise
    raise RuntimeError("Failed to execute after several retries")

def process_rows(ids, worker_id, cfg: globals.Config):
    from browser.browser import Browser
    from office_sud_kz.auth import auth, is_authorized
    from office_sud_kz.isk.main import run as iskRun

    print(f"[Worker {worker_id}] starting browser...")
    browser = Browser()
    while True:
        try:
            browser.main_office_sud_kz()
            auth(browser, cfg)
            break
        except Exception:
            continue

    # if not is_authorized(browser):
    #     print(f"[Worker {worker_id}] Не авторизован!")
    #     browser.driver.quit()
    #     return

    connection = sqlite3.connect(cfg.get('db_name'), timeout=30)
    connection.execute("PRAGMA journal_mode=WAL;")
    connection.execute("PRAGMA synchronous=NORMAL;")
    connection.execute("PRAGMA busy_timeout = 5000;")
    connection.row_factory = sqlite3.Row
    table_name = cfg.get('table_name') 
    placeholder = ','.join('?' * len(ids))
    rows = connection.execute(f"SELECT * FROM {table_name} WHERE id in ({placeholder})", ids).fetchall()

    for row in rows:
        if int(row['id']) % 10 == 0:
            browser.main_office_sud_kz()
        number = row['number'] 
        excel_line_number = row['excel_line_number']
        data = types[cfg.get('type')].get_data(row, cfg)

        print(f"[Worker {worker_id}] row: {excel_line_number} -> {number}")
        if type(data) is str:
            safe_execute(connection, f"UPDATE {table_name} SET status = ?, status_text = ? WHERE id = ?", ('skipped', data, row['id']))
            # cursor.execute(f"UPDATE {table_name} SET status = ?, status_text = ? WHERE id = ?", 
            #                 ('skipped', 'Data is None', row['id']))
            continue
        
        while True:
            try:
                iskRun(browser, data, worker_id)
                safe_execute(connection, f"UPDATE {table_name} SET status = ?, status_text = ? WHERE id = ?", ('success', '', row['id']))
                # cursor.execute(f"UPDATE {table_name} SET status = ?, status_text = ? WHERE id = ?", 
                #                ('success', '', row['id']))
            except Exception as e:
                safe_execute(connection, f"UPDATE {table_name} SET status = ?, status_text = ? WHERE id = ?", ('error', str(e), row['id']))
                # cursor.execute(f"UPDATE {table_name} SET status = ?, status_text = ? WHERE id = ?", 
                #                ('error', str(e), row['id']))
            break

    connection.commit()
    connection.close()
    browser.driver.quit()


def main():
    options = ", ".join(f"{k} - {v.label()}" for k, v in types.items())
    try:
        type = int(input(f"Введите тип флоу: ({options}): "))
        if type not in types.keys():
            print("Неправильный тип флоу: ", type)
            return
    except Exception:
        print("Неправильный тип флоу!")
        return

    print('Открываем файл config.txt...')
    try:
        cfg = globals.Config().load_config()
        print('Конфигурация загружена!')
    except Exception as e:
        print("Файл config.txt не найден!")
        return

    # migration
    cfg.data['type'] = type
    type = types[type]
    cfg.data['table_name'] = type.table_name()
    type.migration(cfg.get('db_name'))

    # db + insert
    wb = load_workbook(cfg.get('file'))
    sheet = wb.active
    rows = list(enumerate(sheet.iter_rows(min_row=2, values_only=False), start=2))

    connection = sqlite3.connect(cfg.get('db_name') )
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    for i, row in rows:
        type.insert(row, cfg, cursor, i)

    connection.commit()        
    table_name = type.table_name()
    ids = [r[0] for r in cursor.execute(f"SELECT id FROM {table_name} WHERE status != ?", ('success',))]
    connection.close()

    n_workers = int(cfg.get("count_process") or 1)
    chunk_size = len(ids) // n_workers + 1
    chunks = [ids[i:i + chunk_size] for i in range(0, len(ids), chunk_size)]

    processes = []
    for wid, chunk in enumerate(chunks):
        p = Process(target=process_rows, args=(chunk, wid, cfg))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    base, ext = os.path.splitext(cfg.get('file'))
    dst_file = f"{base}_biba{ext}"
    shutil.copy(cfg.get('file'), dst_file)   

    connection = sqlite3.connect(cfg.get('db_name'))
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    table_name = type.table_name()
    rows = cursor.execute(f"SELECT excel_line_number, status, status_text FROM {table_name}").fetchall()
    connection.close()
    
    wb = load_workbook(dst_file)
    sheet = wb.active

    for row in rows:
        line_number = row['excel_line_number']
        status = row['status']
        status_text = row['status_text']

        sheet.cell(row=line_number, column=cfg.index('excel_status') + 1, value=status)
        sheet.cell(row=line_number, column=cfg.index('excel_status_text') + 1, value=status_text)

    wb.save(dst_file)
if __name__ == "__main__":
    multiprocessing.freeze_support()  # important for PyInstaller
    main()

    input("Готово!")
