# Cкачиванием файлов с ск Письмо
from flow_types.baseWithoutExcel import WithoutExcelType
from office_sud_kz.clearRequest.main import run as clearRequestRun
from office_sud_kz.clearRequest.smart_clear_request import run as smartClearRequestRun

class ClearRequestType(WithoutExcelType):
    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = value

    # даты включительно
    def label(self):
        return 'Удаление всех ожидающих отправки дел'

    def table_name(self):
        return 'clear_request'

    def migration(self):
        pass

    def insert(self, data, connection):
        pass

    def start(self):
        from office_sud_kz.auth import auth

        types = {
            1: 'Удаление всех ожидающих отправки дел',
            2: 'Умное удаление',
        }
        options = ".\n".join(f"{k} -> {v}" for k, v in types.items())
        try:
            print('==========================')
            print(options)
            print('==========================')

            self.type = int(input(f"Введите тип флоу: "))
            if self.type not in types.keys():
                print("Неправильный тип флоу: ", self.type)
                return
        except Exception as e:
            print("Неправильный тип флоу!")
            return

        browser = self.browser()

        while True:
            try:
                browser.main_office_sud_kz()
                auth(browser, self.cfg)
                break
            except Exception:
                continue

        if self.type == 1:
            clearRequestRun(browser)
        elif self.type == 2:
            smartClearRequestRun(browser)
