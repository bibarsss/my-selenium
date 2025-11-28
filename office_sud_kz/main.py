from multiprocessing import Process
from openpyxl import load_workbook
import globals
import sqlite3
from flow_types.available_types import types 
from flow_types.base import Type

def run():
    print('Открываем файл config.txt...')
    try:
        cfg = globals.Config().load_config()
        print('Конфигурация загружена!')
    except Exception as e:
        print("Файл config.txt не найден!")
        return

    options = ",\n".join(f"{k} -> {v().label()}" for k, v in types.items())
    full_options = options + ",\n111 -> Перезапуск если не получил файл"
    try:
        print('==========================')
        print(full_options)
        print('==========================')
        type = int(input(f"Введите тип флоу: "))
        if str(type) == '111':
            print('==========================')
            print(options)
            print('==========================')
            type = int(input(f"Введите тип флоу перезапуска для получение обработанных строк: "))
            type = types[type](cfg)
            type.save_to_excel()
            return

        if type not in types.keys():
            print("Неправильный тип флоу: ", type)
            return
    except Exception as e:
        print("Неправильный тип флоу!")
        return

    type = types[type](cfg)
    type.start()