# Cкачиванием файлов с ск Письмо
from multiprocessing import Process
import os
import sqlite3
import time

import requests
import urllib3
from common.sqlite import safe_execute
from flow_types.baseWithoutExcel import WithoutExcelType
from globals import RETRY_COUNT
from office_sud_kz.clearRequest.main import run as clearRequestRun

class ClearRequestType(WithoutExcelType):
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
        browser = self.browser()

        while True:
            try:
                browser.main_office_sud_kz()
                auth(browser, self.cfg)
                break
            except Exception:
                continue

        clearRequestRun(browser)

