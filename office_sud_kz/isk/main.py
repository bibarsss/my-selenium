from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from . import step0, step1
from browser.browser import Browser
from common.button import clickByText

import time

def run(browser: Browser):
    while not htmlHasText(browser, "Подача документа в судебный орган"):
        new_form_button = browser.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/new/form/send/index.xhtml']")))
        new_form_button.click()
        time.sleep(1)

    step0.run(browser)
    step1.run(browser)
    return


    #otvet4ik
    bin = "220440007472"
    iin = "950515300621"
    fact_address = "КАЗАХСТАН, Алматинская область, Илиийский"



def htmlHasText(browser: Browser, text: str) -> bool:
    try:
        WebDriverWait(browser.driver, 0.1).until(EC.presence_of_element_located((By.XPATH, f'//*[contains(text(), "{text}")]')))
        return True
    except:
        return False