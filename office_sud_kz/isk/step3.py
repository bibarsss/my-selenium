from common.input_text import textByLabel
from common.button import clickByText
from common.input_upload import uploadFile, uploadAllFilesInDirectory
from common.read_pdf import read
from browser.browser import Browser
import re
import os
from pathlib import Path

from globals import RETRY_COUNT

def run(browser: Browser, data)->bool:
    isk_file_common = Path(data['isk_file_path'])
    isk_file_real = Path(data['isk_file_realpath'])

    if not isk_file_real.exists():
        if not isk_file_common.exists():
            raise Exception("File not found! " + data['isk_file_path'])
        isk_file_common.rename(isk_file_real)

    parsed = parse_claim(read(os.path.abspath(data['isk_file_realpath'])))

    textByLabel(browser, 'Исковые требования', parsed['prosim_block'])
    textByLabel(browser, 'Обстоятельства, на которых основаны требования, и доказательства, подтверждающие эти обстоятельства', parsed['contract_block'])
    browser.wait_for_loader_done()

    uploadFile(browser, data['isk_file_realpath'], "selectLawsuitScanUploader")
    browser.wait_for_loader_done()
    uploadAllFilesInDirectory(browser, data['dir'], 'selectFileUploader')
    browser.wait_for_loader_done()

    c = 0
    while not browser.htmlHasText("Предпросмотр электронного бланка"):
        c += 1
        if c == RETRY_COUNT:
            raise Exception("Ошибка в step3")
        clickByText(browser, 'a' ,'Далее')
        browser.wait_for_loader_done()

    return True

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