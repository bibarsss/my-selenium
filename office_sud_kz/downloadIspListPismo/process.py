from datetime import datetime
import sqlite3
import time
from selenium.webdriver.common.by import By
from browser.browser import Browser
from common.button import clickByText
from .parse_link import run as parse_links
from flow_types.base import Type

def run(browser: Browser, start: datetime, end: datetime, type: Type):
    items = browser.driver.find_elements(By.CSS_SELECTOR, ".case-item-container")

    first, last = get_first_last_date(items)
    first = datetime.strptime(first, "%d.%m.%Y %H:%M")
    last = datetime.strptime(last, "%d.%m.%Y %H:%M")

    if first < start and last < start:
        # остановитесь
        return True
    elif first > end and last > end:
        # иди на след страницу
        return False

    connection = sqlite3.connect(type.cfg.get('db_name'), timeout=30)
    connection.execute("PRAGMA journal_mode=WAL;")
    connection.execute("PRAGMA synchronous=NORMAL;")
    connection.execute("PRAGMA busy_timeout = 5000;")
    connection.row_factory = sqlite3.Row

    count_items = len(items)
    for i in range(count_items):
        go_to_page(browser)
        items = browser.driver.find_elements(By.CSS_SELECTOR, ".case-item-container")
        item = items[i]

        item_date = extract_date(item)
        item_date = datetime.strptime(item_date, "%d.%m.%Y %H:%M")
        if item_date < start or item_date > end:
            continue

        number = extract_number(item)
        item.click()
        browser.wait_for_loader_done()
        while not browser.htmlHasText('Файлы'):
            browser.refresh()
            go_to_page(browser)

            items = browser.driver.find_elements(By.CSS_SELECTOR, ".case-item-container")
            items[i].click()
            browser.wait_for_loader_done()

        links = parse_links(browser, number)
        type.insert(links, connection)
        go_to_page(browser)
        browser.wait_for_loader_done()

    connection.commit()
    connection.close()
    return False

def go_to_page(browser: Browser):
    clickByText(browser, "a", "Полученные письма")
    browser.wait_for_loader_done()
    while not browser.tagWithTextHasClass('a', 'Полученные письма', 'active'):
        clickByText(browser, "a", "Полученные письма")
        browser.wait_for_loader_done()
        time.sleep(1)

def get_first_last_date(items):
    if not items:
        first_date = None
        last_date = None
    else:
        first_date = extract_date(items[0])
        last_date = extract_date(items[-1])

    return (first_date, last_date)

def extract_date(item):
    rows = item.find_elements(By.CSS_SELECTOR, ".row")
    for row in rows:
        desc = row.find_element(By.CSS_SELECTOR, ".desc").text.strip()
        if desc == "Дата отправки:":
            return row.find_element(By.CSS_SELECTOR, ".flex-1").text.strip()
    return None

def extract_number(item):
    return item.find_element(By.TAG_NAME, "h3").text.strip()

def get_current_page(browser):
    try:
        el = browser.driver.find_element(By.CSS_SELECTOR, ".list-pages span.current")
        return int(el.text.strip())
    except Exception:
        return None
