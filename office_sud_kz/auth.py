from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from common.input_text import textByPlaceholder, textIsSetByPlaceholder
from common.button import clickByValue, clickByIndex
from browser.browser import Browser
import globals
import time

def auth(browser: Browser, cfg: globals.Config):
    while not is_rus_selected(browser):
        clickByIndex(browser, "div.lang a", 1)
        browser.wait_for_loader_done()
        time.sleep(1)

    while not textIsSetByPlaceholder(browser, "ИИН/БИН", cfg.get('iin')) and not textByPlaceholder(browser, "Пароль", cfg.get('password')):
        textByPlaceholder(browser, "ИИН/БИН", cfg.get('iin'))
        textByPlaceholder(browser, "Пароль", cfg.get('password'))
        browser.wait_for_loader_done()

    clickByValue(browser, 'Войти')
    browser.wait_for_loader_done()

def is_authorized(browser: Browser) -> bool:
    try:
        WebDriverWait(browser.driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.profile")))
        return True
    except TimeoutException:
        return False

def is_rus_selected(browser: Browser):
    try:
        rus_element = WebDriverWait(browser.driver, 1).until(EC.presence_of_element_located((By.XPATH,'//div[@class="lang flex flex-center"]//a[text()="РУС"]')))
        return 'active' in rus_element.get_attribute('class')
    except:
        return False