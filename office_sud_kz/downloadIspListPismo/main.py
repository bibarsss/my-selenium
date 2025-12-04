from datetime import datetime
from browser.browser import Browser
from common.button import clickByText
from globals import RETRY_COUNT
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from . import process
from flow_types.base import Type

def run(browser: Browser, data: dict, type: Type):
    c = 0
    while not browser.htmlHasText("Отправка писем"):
        c += 1
        if c == RETRY_COUNT:
            raise Exception("Ошибка при октрытии страницы Мои письма")
        browser.wait_for_loader_done()
        new_form_button = browser.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/form/letter/info.xhtml']")))
        browser.wait_for_loader_done()
        new_form_button.click()
        browser.wait_for_loader_done()

    c = 0
    while not browser.tagWithTextHasClass('a', 'Полученные письма', 'active'):
        c += 1
        if c == RETRY_COUNT:
            raise Exception("Ошибка при октрытии страницы Мои письма")
        clickByText(browser, "a", "Полученные письма")
        browser.wait_for_loader_done()

    if not get_current_page(browser):
        raise Exception("Письма не найдены!")

    start = datetime.strptime(data['main_date_start'], "%d.%m.%Y")
    end = datetime.strptime(data['main_date_end'], "%d.%m.%Y")

    while True:
        if not ableToProcess(browser, data):
            if not nextPageButtonExists(browser):
                break
            clickByText(browser, "a", "►")
            browser.wait_for_loader_done()
            continue

        # obrabotka
        try:
            shouldStop = process.run(browser, start, end, type)
        except Exception:
            continue

        if shouldStop:
            break

        if not nextPageButtonExists(browser):
            break
        clickByText(browser, "a", "►")
        browser.wait_for_loader_done()

def nextPageButtonExists(browser: Browser) -> bool:
    try:
        browser.driver.find_element(By.XPATH, "//div[contains(@class,'list-pages')]//a[text()='►']")
        return True
    except Exception:
        return False

def get_current_page(browser: Browser):
    try:
        el = browser.driver.find_element(By.CSS_SELECTOR, ".list-pages span.current")
        return int(el.text.strip())
    except Exception:
        return None

def ableToProcess(browser: Browser, data: dict):
    current_page = get_current_page(browser)
    while not current_page:
        browser.refresh()
        current_page = get_current_page(browser)

    if current_page%data['n_workers'] == data['worker_id']:
        print('[Worker ' + str(data['worker_id']) + '] - ', current_page, 'страница')
        return True

    return False

