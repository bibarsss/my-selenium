from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from common.input_select import selectByLabel, selectByLabelOnModal, isSelectedByLabel, isSelectedByLabelOnModal
from common.button import clickByValue, clickByText, clickButtonByRow, clickFooterButtonByValue
from common.input_text import textModalByRow
from browser.browser import Browser
from common.podsudnost import getPodsudnostValue

def run(browser: Browser, data)->bool:
    while not isSelectedByLabel(browser, "Характер заявления", "1") \
            or not isSelectedByLabel(browser, "Категория дела", "151"):
        selectByLabel(browser, "Категория дела", "151")
        browser.wait_for_loader_done()
        selectByLabel(browser, "Характер заявления", "1")
        browser.wait_for_loader_done()

    browser.refresh()
# юрлицо взыскатель 
    while not isModalOpened(browser, 'selectSideModalDialog'):
        clickByText(browser, 'button', 'Добавить участника процесса')
        browser.wait_for_loader_done()

    divId = "jurModalDialog"
    while not isModalOpened(browser, divId):
        while not isSelectedByLabelOnModal(browser, "Тип лица", "true"):
            selectByLabelOnModal(browser, "Тип лица", "true")
            browser.wait_for_loader_done()

        clickByValue(browser, "Далее")
        browser.wait_for_loader_done()

    while not verifyModalRowValue(browser, divId, 4, data['bin']) \
        or not verifyModalRowValue(browser, divId, 7, data['address']) \
        or not verifyModalRowValue(browser, divId, 8, data['detail']):

        textModalByRow(browser, divId, 4, data['bin'])
        browser.wait_for_loader_done()
        clickButtonByRow(browser, divId, 4)
        browser.wait_for_loader_done()
        textModalByRow(browser, divId, 7, data['address'])
        browser.wait_for_loader_done()
        textModalByRow(browser, divId, 8, data['detail'])
        browser.wait_for_loader_done()

    clickFooterButtonByValue(browser, divId, "Сохранить")
    browser.wait_for_loader_done()

    browser.refresh()
# представитель
    while not isModalOpened(browser, 'selectSideModalDialog'):
        clickByText(browser, 'button', 'Добавить участника процесса')
        browser.wait_for_loader_done()

    browser.wait_for_loader_done()
    divId = "fizModalDialog"
    
    while not isModalOpened(browser, divId):
        while not isSelectedByLabelOnModal(browser, "Сторона процесса", "5"):
            selectByLabelOnModal(browser, "Сторона процесса", "5")
            browser.wait_for_loader_done()

        browser.wait_for_loader_done()
        clickByValue(browser, "Далее")
        browser.wait_for_loader_done()

    while not verifyModalRowValue(browser, divId, 3, data['iin']) \
        and not verifyModalRowValue(browser, divId, 9, data['phone']):
        textModalByRow(browser, divId, 3, data['iin'])  
        browser.wait_for_loader_done()
        clickButtonByRow(browser, divId, 3)
        browser.wait_for_loader_done()
        textModalByRow(browser, divId, 9, data['phone'])  
        browser.wait_for_loader_done()

    clickFooterButtonByValue(browser, divId, "Сохранить")
    browser.wait_for_loader_done()
    
    browser.refresh()
# должник 
    while not isModalOpened(browser, 'selectSideModalDialog'):
        clickByText(browser, 'button', 'Добавить участника процесса')
        browser.wait_for_loader_done()

    divId = "fizModalDialog"
    while not isModalOpened(browser, divId):
        while not isSelectedByLabelOnModal(browser, "Сторона процесса", "2"):
            selectByLabelOnModal(browser, "Сторона процесса", "2")
            browser.wait_for_loader_done()

        clickByValue(browser, "Далее")
        browser.wait_for_loader_done()

    while not verifyModalRowValue(browser, divId, 3, data['iin_dolzhnik']): 
        textModalByRow(browser, divId, 3, data['iin_dolzhnik'])
        browser.wait_for_loader_done()
        clickButtonByRow(browser, divId, 3)
        browser.wait_for_loader_done()

    clickFooterButtonByValue(browser, divId, "Сохранить")
    browser.wait_for_loader_done()

    browser.refresh()

    podsudnost = getPodsudnostValue(data['podsudnost'])
    sudValue = podsudnost['sudValue']
    sudName = podsudnost['sudName']
    oblastValue = podsudnost['oblastValue']

    if not bool(sudValue) or not bool(sudName):
        raise Exception('Подсудность в справочнике не найдены')
    
    while not isSelectedByLabel(browser, "Область (столица, город республиканского значения)", oblastValue) or not isSelectedByLabel(browser, "Судебный орган", sudValue):
        selectByLabel(browser, "Область (столица, город республиканского значения)", oblastValue)
        browser.wait_for_loader_done()
        if not browser.htmlHasText(sudName):
            continue
        browser.wait_for_loader_done()

        selectByLabel(browser, "Судебный орган", sudValue)
        browser.wait_for_loader_done()

    while not browser.htmlHasText("Информация об оплате"):
        clickByText(browser, 'a' ,'Далее')
        browser.wait_for_loader_done()

    return True

def isModalOpened(browser: Browser, modal_id: str) -> bool:
    try:
        modal = browser.driver.find_element(By.ID, modal_id)
        return "in" in modal.get_attribute("class").split()
    except:
        return False
    
def verifyModalRowValue(browser: Browser, div_id: str, row_index: int, expected: str) -> bool:
    xpath = f"(//div[@id='{div_id}']//tbody/tr)[{row_index}]//input | (//div[@id='{div_id}']//tbody/tr)[{row_index}]//textarea"
    el = browser.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    actual = el.get_attribute("value") or el.text
    is_ok = (actual.strip() == expected.strip())
    return is_ok