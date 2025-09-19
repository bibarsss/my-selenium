from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from common.input_select import selectByLabel, isSelectedByLabel
from common.input_text import textByLabel
from common.button import clickByText
from common.input_upload import uploadFile
from browser.browser import Browser
import globals
import time

def run(browser: Browser)->bool:
    while not isSelectedByLabel(browser, 'КБК', '2'):
        selectByLabel(browser, 'КБК', '2')
        browser.wait_for_loader_done()

    textByLabel(browser, 'Сумма иска', globals.globalData['summaIska'])
    textByLabel(browser, 'Сумма государственной пошлины (для расчета воспользуйтесь калькулятором, нажав на иконку в поле ввода)', globals.globalData['powlina'])

    uploadFile(browser, globals.globalData['powlina_file_path'], 'selectPaymentScanUploader1')
    browser.wait_for_loader_done()

    while not htmlHasText(browser, "Данные для электронного бланка"):
        clickByText(browser, 'a' ,'Далее')
        browser.wait_for_loader_done()

    return True

def htmlHasText(browser: Browser, text: str) -> bool:
    try:
        WebDriverWait(browser.driver, 0.1).until(EC.presence_of_element_located((By.XPATH, f'//*[contains(text(), "{text}")]')))
        return True
    except:
        return False