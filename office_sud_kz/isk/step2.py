from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from common.input_select import selectByLabel, isSelectedByLabel
from common.input_text import textByLabel
from common.button import clickByText
from common.input_upload import uploadFile
from browser.browser import Browser
import time

def run(browser: Browser)->bool:
    # return True
    while not isSelectedByLabel(browser, 'КБК', '2'):
        selectByLabel(browser, 'КБК', '2')
        time.sleep(1)

    summaIska = 180000
    powlina = 5812
    textByLabel(browser, 'Сумма иска', str(summaIska))
    textByLabel(browser, 'Сумма государственной пошлины (для расчета воспользуйтесь калькулятором, нажав на иконку в поле ввода)', str(powlina))

    uploadFile(browser, 'a.pdf', 'selectPaymentScanUploader1')

    while not htmlHasText(browser, "Данные для электронного бланка"):
            clickByText(browser, 'a' ,'Далее')
            time.sleep(1)

    return True

def htmlHasText(browser: Browser, text: str) -> bool:
    try:
        WebDriverWait(browser.driver, 0.1).until(EC.presence_of_element_located((By.XPATH, f'//*[contains(text(), "{text}")]')))
        return True
    except:
        return False