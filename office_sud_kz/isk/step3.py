from common.input_text import textByLabel
from common.button import clickByText
from common.input_upload import uploadFile, uploadAllFilesInDirectory
from common.read_pdf import read
from browser.browser import Browser
import re
import os
from pathlib import Path
import time

from globals import RETRY_COUNT

def run(browser: Browser, data)->bool:
    if data['type'] == 1:
        isk_file_common = Path(data['rows'][0]['isk_file_path'])
        isk_file_real = Path(data['rows'][0]['isk_file_realpath'])
    else:
        isk_file_common = Path(data['rows'][0]['isk_many_file_path'])
        isk_file_real = Path(data['rows'][0]['isk_many_file_path'])

    if not isk_file_real.exists():
        if not isk_file_common.exists():
            raise Exception("File not found! " + str(isk_file_common))
        isk_file_common.rename(isk_file_real)

    parsed = parse_claim(read(str(isk_file_real.resolve())))

    textByLabel(browser, 'Исковые требования', parsed['prosim_block'])
    textByLabel(browser, 'Обстоятельства, на которых основаны требования, и доказательства, подтверждающие эти обстоятельства', parsed['contract_block'])
    browser.wait_for_loader_done()

    uploadFile(browser, str(isk_file_real), "selectLawsuitScanUploader")
    browser.wait_for_loader_done()

    for row in data['rows']:
        uploadAllFilesInDirectory(browser, row['dir'], 'selectFileUploader')
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
