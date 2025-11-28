from common.input_select import selectByLabel, isSelectedByLabel
from common.input_text import textByLabel
from common.button import clickByText
from common.input_upload import uploadFile
from browser.browser import Browser
from globals import RETRY_COUNT

def run(browser: Browser, data)->bool:
    c = 0
    while not isSelectedByLabel(browser, 'КБК', '2'):
        c += 1
        if c == RETRY_COUNT:
            raise Exception("Ошибка в step2")
        selectByLabel(browser, 'КБК', '2')
        browser.wait_for_loader_done()

    textByLabel(browser, 'Сумма иска', data['summaIska'])
    textByLabel(browser, 'Сумма государственной пошлины (для расчета воспользуйтесь калькулятором, нажав на иконку в поле ввода)', data['powlina'])

    uploadFile(browser, data['powlina_file_path'], 'selectPaymentScanUploader1')
    browser.wait_for_loader_done()

    c = 0
    while not browser.htmlHasText("Данные для электронного бланка"):
        c += 1
        if c == RETRY_COUNT:
            raise Exception("Ошибка в step2")
        clickByText(browser, 'a' ,'Далее')
        browser.wait_for_loader_done()

    return True