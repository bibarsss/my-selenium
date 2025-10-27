from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from common.input_select import selectByLabel, isSelectedByLabel
from common.button import clickByValue
from browser.browser import Browser

def run(browser: Browser, data):
    while not isSelectedByLabel(browser, "Тип производства", "CIVIL") or not isSelectedByLabel(browser, "Инстанция", "FIRSTINSTANCE") or not isSelectedByLabel(browser, "Тип документа", "1000"):
        selectByLabel(browser, "Тип производства", "CIVIL")
        browser.wait_for_loader_done()
        selectByLabel(browser, "Инстанция", "FIRSTINSTANCE")
        browser.wait_for_loader_done()
        selectByLabel(browser, "Тип документа", "1000")
        browser.wait_for_loader_done()

    while not browser.htmlHasText("1.Заполнение данных"):
        clickByValue(browser, 'Отправить')
        browser.wait_for_loader_done()
    