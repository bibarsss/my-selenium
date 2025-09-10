from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from common.input_select import selectByLabel, isSelectedByLabel
from common.button import clickByValue
from browser.browser import Browser
import time

def run(browser: Browser)->bool:
    while not isSelectedByLabel(browser, "Тип производства", "CIVIL") or not isSelectedByLabel(browser, "Инстанция", "FIRSTINSTANCE") or not isSelectedByLabel(browser, "Тип документа", "3"):
        selectByLabel(browser, "Тип производства", "CIVIL")
        selectByLabel(browser, "Инстанция", "FIRSTINSTANCE")
        selectByLabel(browser, "Тип документа", "3")
        time.sleep(1)

    while not htmlHasText(browser, "Заявление искового, особого производства"):
        clickByValue(browser, 'Отправить')
        time.sleep(1)
    
    return True

def htmlHasText(browser: Browser, text: str) -> bool:
    try:
        WebDriverWait(browser.driver, 0.1).until(EC.presence_of_element_located((By.XPATH, f'//*[contains(text(), "{text}")]')))
        return True
    except:
        return False