from browser.browser import Browser
from . import search, parse

import time

def run(browser: Browser, data, worker_id):
    browser.wait_for_loader_done()

    while not browser.htmlHasText('Фильтр'):
        browser.safe_get('https://office.sud.kz/form/cases/mycases.xhtml')
        browser.wait_for_loader_done()
        time.sleep(2)

    print(f'[Worker {worker_id}] searching...')
    search.run(browser, data)

    print(f'[Worker {worker_id}] parsing...')
    return parse.run(browser, data)
