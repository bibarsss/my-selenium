from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from common.input_text import textByPlaceholder, textIsSetByPlaceholder
from common.button import clickByValue, clickByIndex
from browser.browser import Browser

import time

def auth(browser: Browser)->bool:
    browser.safe_get("https://office.sud.kz/")

    iin = "010213500250"
    password = "Utepov2025!@#"

    while not is_rus_selected(browser):
        clickByIndex(browser, "div.lang a", 1)
        time.sleep(1)

    while not textIsSetByPlaceholder(browser, "ИИН/БИН", iin) and not textByPlaceholder(browser, "Пароль", password):
        textByPlaceholder(browser, "ИИН/БИН", iin)
        textByPlaceholder(browser, "Пароль", password)
        time.sleep(1)

    clickByValue(browser, 'Войти')

    return is_authorized(browser)

def is_authorized(browser: Browser) -> bool:
    try:
        browser.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.profile")))
        return True
    except TimeoutException:
        return False

def is_rus_selected(browser: Browser):
    try:
        rus_element = WebDriverWait(browser.driver, 1).until(
            EC.presence_of_element_located((
                By.XPATH,
                '//div[@class="lang flex flex-center"]//a[text()="РУС"]'
            ))
        )
        return 'active' in rus_element.get_attribute('class')
    except:
        return False