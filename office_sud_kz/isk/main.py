from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from . import step0, step1, step2, step3, step4
from browser.browser import Browser

def run(browser: Browser, data, worker_id):
    browser.wait_for_loader_done()
    browser.main_office_sud_kz()
    browser.wait_for_loader_done()

    while not htmlHasText(browser, "Подача документа в судебный орган"):
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

    print(f'[Worker {worker_id}] step 4')
    step4.run(browser, data)
    
    return




def htmlHasText(browser: Browser, text: str) -> bool:
    try:
        WebDriverWait(browser.driver, 0.1).until(EC.presence_of_element_located((By.XPATH, f'//*[contains(text(), "{text}")]')))
        return True
    except:
        return False