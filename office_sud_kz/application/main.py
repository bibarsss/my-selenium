from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from browser.browser import Browser
from selenium.webdriver.support import expected_conditions as EC
from globals import RETRY_COUNT
from . import step0, step1, step2, step3


def run(browser: Browser, data, worker_id):
    browser.wait_for_loader_done()
    browser.main_office_sud_kz()
    browser.wait_for_loader_done()

    c = 0
    while not browser.htmlHasText('Подача документа в судебный орган'):
        c += 1
        if c == RETRY_COUNT:
            raise Exception("Ошибка в начале")
        browser.wait_for_loader_done()
        new_form_button = browser.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/form/send/index.xhtml']")))
        browser.wait_for_loader_done()
        new_form_button.click()
        browser.wait_for_loader_done()

    print(f'[Worker {worker_id}] step 0')
    step0.run(browser, data)

    print(f'[Worker {worker_id}] step 1')
    step1.run(browser, data)
    
    print(f'[Worker {worker_id}] step 2')
    step2.run(browser, data)

    print(f'[Worker {worker_id}] step 3')
    step3.run(browser, data)