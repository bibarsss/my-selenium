import time
from common.download import downloadByLabel
from browser.browser import Browser

def run(browser: Browser, data)->bool:
    downloadByLabel(browser, "Предпросмотр электронного бланка", data['rows'][0]['blank_path'], "blank.pdf")

    return True
