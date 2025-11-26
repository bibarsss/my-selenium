from common.input_select import selectByLabel, isSelectedByLabel
from common.input_text import textByLabel
from common.button import clickByText
from common.input_upload import uploadFile
from browser.browser import Browser
import time

def run(browser: Browser, data)->bool:
    while not isSelectedByLabel(browser, 'КБК', '2'):
        selectByLabel(browser, 'КБК', '2')
        browser.wait_for_loader_done()

    textByLabel(browser, 'Сумма, подлежащая взысканию', data['summaIska'])
    textByLabel(browser, 'Сумма государственной пошлины (для расчета воспользуйтесь калькулятором, нажав на иконку в поле ввода)', data['powlina'])

    uploadFile(browser, data['powlina_file_path'], 'selectPaymentScanUploader1')
    browser.wait_for_loader_done()

    while not browser.htmlHasText("Данные для электронного бланка"):
        clickByText(browser, 'a' ,'Далее')
        browser.wait_for_loader_done()

    return True
