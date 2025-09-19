from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from common.input_select import selectByLabel, isSelectedByLabel
from common.input_text import textByLabel
from common.button import clickByText
from common.input_upload import uploadFile, uploadAllFilesInDirectory
from common.read_pdf import read
from browser.browser import Browser
import time
import re
import os

def run(browser: Browser)->bool:
    parsed = parse_claim(read(os.path.abspath("b.pdf")))
    textByLabel(browser, 'Исковые требования', parsed['prosim_block'])
    textByLabel(browser, 'Обстоятельства, на которых основаны требования, и доказательства, подтверждающие эти обстоятельства', parsed['contract_block'])
    browser.wait_for_loader_done()

    uploadFile(browser, "a.pdf", "selectLawsuitScanUploader")
    browser.wait_for_loader_done()
    directory = "arch/Байзакский районный суд Жамбылской области/Иск 1"
    uploadAllFilesInDirectory(browser, directory, 'selectFileUploader')
    browser.wait_for_loader_done()

    while not htmlHasText(browser, "Предпросмотр электронного бланка"):
        clickByText(browser, 'a' ,'Далее')
        browser.wait_for_loader_done()

    return True

def htmlHasText(browser: Browser, text: str) -> bool:
    try:
        WebDriverWait(browser.driver, 0.1).until(EC.presence_of_element_located((By.XPATH, f'//*[contains(text(), "{text}")]')))
        return True
    except:
        return False

def parse_claim(text: str):
    result = {}

    contract_pattern = r"(\d{2}\.\d{2}\.\d{4} года.*?)(?=На основании изложенного)"
    contract_match = re.search(contract_pattern, text, re.S | re.I)
    if contract_match:
        result["contract_block"] = contract_match.group(1).strip()

    prosim_pattern = r"(На основании изложенного.*?)(?:ПРИЛОЖЕНИЕ|$)"
    prosim_match = re.search(prosim_pattern, text, re.S | re.I)
    if prosim_match:
        result["prosim_block"] = prosim_match.group(1).strip()

    return result