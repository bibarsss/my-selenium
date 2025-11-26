from common.download import downloadByLabel
from browser.browser import Browser

def run(browser: Browser, data)->bool:
    downloadByLabel(browser, "Предпросмотр электронного бланка", data['dir'], "blank.pdf")
    
    return True
