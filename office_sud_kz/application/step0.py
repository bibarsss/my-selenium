from common.input_select import selectByLabel, isSelectedByLabel
from common.button import clickByValue
from browser.browser import Browser
from globals import RETRY_COUNT

def run(browser: Browser, data):
    c = 0
    while not isSelectedByLabel(browser, "Тип производства", "CIVIL") or not isSelectedByLabel(browser, "Инстанция", "FIRSTINSTANCE") or not isSelectedByLabel(browser, "Тип документа", "1000"):
        c += 1
        if c == RETRY_COUNT:
            raise Exception("Ошибка в step0")
        selectByLabel(browser, "Тип производства", "CIVIL")
        browser.wait_for_loader_done()
        selectByLabel(browser, "Инстанция", "FIRSTINSTANCE")
        browser.wait_for_loader_done()
        selectByLabel(browser, "Тип документа", "1000")
        browser.wait_for_loader_done()

    while not browser.htmlHasText("1.Заполнение данных"):
        clickByValue(browser, 'Отправить')
        browser.wait_for_loader_done()
    