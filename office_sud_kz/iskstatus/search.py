import time
from common.input_text import textByLabel
from common.button import clickByValue, clickByIndex
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from browser.browser import Browser
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

def run(browser: Browser, data):
    if (
        data['talon'] is None
        or data['talon'] == 'None'
        or not str(data['talon']).isdigit()
    ):
        raise Exception(f"Номер талона в неправильном формате -> {data['talon']}")   

    textByLabel(browser, 'Номер', data['talon']) 
    browser.wait_for_loader_done()

    for i in range(5):
        clickByValue(browser, 'Найти')
        browser.wait_for_loader_done()
        time.sleep(1)
        if has_result(browser):
            break

    if not has_result(browser):
        raise Exception("По талону запись не найдена!")        

    clickByIndex(browser, "div.case-item-container", 0)
    while not htmlHasText(browser, 'Динамика хода рассмотрения дела'):
        time.sleep(1)
        
def htmlHasText(browser: Browser, text: str) -> bool:
    xpath = f'//*[contains(normalize-space(.), "{text.strip()}")]'
    try:
        WebDriverWait(browser.driver, 0.1).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return True
    except Exception:
        return False

def has_result(browser) -> bool:
    try:
        container = browser.driver.find_element(By.CSS_SELECTOR, "span.scrolled-list")
        items = container.find_elements(By.CSS_SELECTOR, "div.case-item-container")
        count = len(items)
        return count == 1
    except (NoSuchElementException, StaleElementReferenceException):
        return False