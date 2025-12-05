import os
from browser.browser import Browser
from selenium.webdriver.common.by import By
from . import parse_links, search, download

import time

def run(browser: Browser, data, worker_id):
    browser.wait_for_loader_done()

    while not browser.htmlHasText('Фильтр'):
        browser.safe_get('https://office.sud.kz/form/cases/mycases.xhtml')
        browser.wait_for_loader_done()
        time.sleep(2)

    data['worker_id'] = worker_id

    print(f'[Worker {worker_id}] searching...')
    search.run(browser, data)

    print(f'[Worker {worker_id}] parsing...')
    file_links = parse_links.run(browser, data)

    print(f'[Worker {worker_id}] downloading...')
    download.run(browser, data, file_links)




