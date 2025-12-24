import globals
from flow_types.available_types import types, excelTypes

def run():
    print('Запуск...')
    try:
        cfg = globals.Config().load_config()
    except Exception as e:
        print("Файл config.txt не найден!")
        cfg = globals.Config()

    options = ".\n".join(f"{k} -> {v().label()}" for k, v in types.items())
    full_options = options + ".\n111 -> Перезапуск если не получил файл."
    try:
        print('==========================')
        print(full_options)
        print('==========================')
        type = int(input(f"Введите тип флоу: "))
        if str(type) == '111':
            print('==========================')
            options = ",\n".join(f"{k} -> {v().label()}" for k, v in excelTypes.items())
            print(options)
            print('==========================')
            type = int(input(f"Введите тип флоу перезапуска для получение обработанных строк: "))
            if type not in excelTypes.keys():
                print("Неправильный тип флоу: ", type)
                return
            type = excelTypes[type](cfg)
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
