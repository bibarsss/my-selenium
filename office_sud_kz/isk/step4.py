from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from common.download import downloadByLabel
from browser.browser import Browser
import time
import re
import os

def run(browser: Browser)->bool:
    downloadByLabel(browser, "Предпросмотр электронного бланка", "as/as", "blank.pdf")
    
    return True

def htmlHasText(browser: Browser, text: str) -> bool:
    try:
        WebDriverWait(browser.driver, 0.1).until(EC.presence_of_element_located((By.XPATH, f'//*[contains(text(), "{text}")]')))
        return True
    except:
        return False

def htmlHasText(browser: Browser, text: str) -> bool:
    try:
        WebDriverWait(browser.driver, 0.1).until(EC.presence_of_element_located((By.XPATH, f'//*[contains(text(), "{text}")]')))
        return True
    except:
        return False
    