from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from common.input_select import selectByLabel, isSelectedByLabel
from common.button import clickByValue
from browser.browser import Browser
import globals
import time

def run(browser: Browser, data)->bool:
    while not isSelectedByLabel(browser, "Тип производства", "CIVIL") or not isSelectedByLabel(browser, "Инстанция", "FIRSTINSTANCE") or not isSelectedByLabel(browser, "Тип документа", "3"):
        selectByLabel(browser, "Тип производства", "CIVIL")
        browser.wait_for_loader_done()
        selectByLabel(browser, "Инстанция", "FIRSTINSTANCE")
        browser.wait_for_loader_done()
        selectByLabel(browser, "Тип документа", "3")
        browser.wait_for_loader_done()

    while not htmlHasText(browser, "Заявление искового, особого производства"):
        clickByValue(browser, 'Отправить')
        browser.wait_for_loader_done()
    
    return True

def htmlHasText(browser: Browser, text: str) -> bool:
    try:
        WebDriverWait(browser.driver, 0.1).until(EC.presence_of_element_located((By.XPATH, f'//*[contains(text(), "{text}")]')))
        return True
    except:
        return False