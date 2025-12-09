from browser.browser import Browser
from common.download import downloadByButtonLabel

def run(browser: Browser, data)->bool:
    downloadByButtonLabel(browser, "Скачать талон об отправке", data['dir'])
    browser.main_office_sud_kz()
    browser.wait_for_loader_done()

    return True
