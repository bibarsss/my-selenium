from multiprocessing import Process
from pathlib import Path
from openpyxl import load_workbook
import globals
import sqlite3
from flow_types.available_types import types 
from flow_types.base import Type

def chunk_list(lst, n):
    k, m = divmod(len(lst), n)
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

def process_rows(ids, worker_id, type: Type):
    from browser.browser import Browser
    from office_sud_kz.auth import auth

    print(f"[Worker {worker_id}] starting...")
    browser = Browser()

    while True:
        try:
            browser.main_office_sud_kz()
            auth(browser, type.cfg)
            break
        except Exception:
            continue

    connection = sqlite3.connect(type.cfg.get('db_name'), timeout=30)
    connection.execute("PRAGMA journal_mode=WAL;")
    connection.execute("PRAGMA synchronous=NORMAL;")
    connection.execute("PRAGMA busy_timeout = 5000;")
    connection.row_factory = sqlite3.Row

    placeholder = ','.join('?' * len(ids))
    rows = connection.execute(f"SELECT * FROM {type.table_name()} WHERE id in ({placeholder})", ids).fetchall()

    for row in rows:
        if int(row['id']) % 10 == 0:
            browser.refresh()

        excel_line_number = row['excel_line_number']
        print(f"[Worker {worker_id}] row: {excel_line_number} -> start")
        type.run(browser, connection, row, worker_id)        

    connection.commit()
    connection.close()
    browser.driver.quit()

def run():
    print('Открываем файл config.txt...')
    try:
        cfg = globals.Config().load_config()
        print('Конфигурация загружена!')
    except Exception as e:
        print("Файл config.txt не найден!")
        return

    options = ", ".join(f"{k} - {v().label()}" for k, v in types.items())
    full_options = options + ", 111 - Перезапуск если не получил файл"
    try:
        type = int(input(f"Введите тип флоу: ({full_options}): "))
        if str(type) == '111':
            type = int(input(f"Введите тип флоу для перезапуска: ({options}): "))
            type = types[type](cfg)
            type.save_to_excel()
            return

        if type not in types.keys():
            print("Неправильный тип флоу: ", type)
            return
    except Exception as e:
        print("Неправильный тип флоу!")
        return

    # migration
    type = types[type](cfg)
    type.migration()
    
    # db + insert
    wb = load_workbook(cfg.get('file'))
    sheet = wb.active
    rows = list(enumerate(sheet.iter_rows(min_row=2, values_only=False), start=2))

    connection = sqlite3.connect(cfg.get('db_name') )
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    for i, row in rows:
        type.insert(row, cursor, i)

    connection.commit()        

    table_name = type.table_name()
    ids = [r[0] for r in cursor.execute(f"SELECT id FROM {table_name} WHERE status != ?", ('success',))]
    connection.close()

    n_workers = int(type.cfg.get("count_process") or 1)
    chunks = chunk_list(ids, n_workers)

    processes = []
    for wid, chunk in enumerate(chunks):
        p = Process(target=process_rows, args=(chunk, wid, type))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    type.save_to_excel()
