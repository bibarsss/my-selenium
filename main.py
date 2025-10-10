import multiprocessing
from multiprocessing import Process
from pathlib import Path
from openpyxl import load_workbook
import globals
from my_types import isk as iskMigration
import sqlite3
import os
os.environ["SELENIUM_MANAGER_NO_BROWSER_DOWNLOAD"] = "1"
types = {
    1: iskMigration,
    # 2: iskMigration
    }
def process_rows(ids, worker_id, cfg: globals.Config):
    from browser.browser import Browser
    from office_sud_kz.auth import auth, is_authorized
    from office_sud_kz.isk.main import run as iskRun

    print(f"[Worker {worker_id}] starting browser...")
    browser = Browser()
    browser.safe_get("https://office.sud.kz/")
    auth(browser, cfg)

    if not is_authorized(browser):
        print(f"[Worker {worker_id}] Не авторизован!")
        browser.driver.quit()
        return

    connection = sqlite3.connect(cfg.get('db_name'))
    connection.row_factory = sqlite3.Row
    table_name = cfg.get('table_name') 
    cursor = connection.cursor()
    placeholder = ','.join('?' * len(ids))
    cursor.execute(f"SELECT * FROM {table_name} WHERE id in ({placeholder})", ids)
    for row in cursor:
        number = row['number'] 
        data = types[cfg.get('type')].get_data(row, cfg)
        print(f"[Worker {worker_id}] {number}")
        print(data)
        if data is None:
            continue
        
        try:
            iskRun(browser, data)
            # print(f"[Worker {worker_id}] {i} -> success")
        except Exception as e:
            # print(f"[Worker {worker_id}] {i} -> exception {e}")
            continue
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
    
    print('enddddddddddddddddddddddd')
        # try:
        #     iskRun(browser)
        #     print(f"[Worker {worker_id}] {i} -> success")
        #     sheet.cell(row=i, column=20, value="success")  # mark in Excel
        # except Exception as e:
        #     print(f"[Worker {worker_id}] {i} -> exception {e}")
        #     sheet.cell(row=i, column=20, value=f"error: {e}")

    # for loop 5 times with chunks

    # wb = load_workbook(cfg.data['file'])
    # sheet = wb.active
    # rows = list(enumerate(sheet.iter_rows(min_row=2, values_only=False), start=2))

    # n_workers = int(cfg.data.get("count_process") or 1)
    # chunk_size = len(rows) // n_workers + 1
    # chunks = [rows[i:i + chunk_size] for i in range(0, len(rows), chunk_size)]

    # processes = []
    # for wid, chunk in enumerate(chunks):
    #     p = Process(target=process_rows, args=(chunk, wid, cfg))
    #     p.start()
    #     processes.append(p)

    # for p in processes:
    #     p.join()


if __name__ == "__main__":
    multiprocessing.freeze_support()  # important for PyInstaller
    main()
