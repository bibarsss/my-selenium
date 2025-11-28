import time
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
    sp_file_common = Path(data['sp_file_path'])
    sp_file_real = Path(data['sp_file_realpath'])

    if not sp_file_real.exists():
        if not sp_file_common.exists():
            raise Exception("File not found! " + data['sp_file_path'])
        sp_file_common.rename(sp_file_real)

    parsed = parse(read(os.path.abspath(data['sp_file_realpath'])))

    textByLabel(browser, 'Предъявляемые требования', parsed['prosim'])
    textByLabel(browser, 'Обстоятельства, на которых основаны требования, и доказательства, подтверждающие эти обстоятельства', parsed['zayavlenie'])
    browser.wait_for_loader_done()

    uploadFile(browser, data['sp_file_realpath'], "selectLawsuitScanUploader")
    browser.wait_for_loader_done()
    time.sleep(2)
    uploadAllFilesInDirectory(browser, data['dir'], 'selectFileUploader')
    browser.wait_for_loader_done()

    c = 0
    while not browser.htmlHasText("Предпросмотр электронного бланка"):
        c += 1
        if c == RETRY_COUNT:
            raise Exception("Ошибка в step0")
        clickByText(browser, 'a' ,'Далее')
        browser.wait_for_loader_done()

    return True
    
def parse(text):
    result = {}

    zayav_pattern = r"О вынесении судебного приказа\s*(.*?)(?=ПРОСИМ\s+СУД:)"
    zayav_match = re.search(zayav_pattern, text, re.S | re.I)
    if zayav_match:
        result["zayavlenie"] = zayav_match.group(1).strip()

    prosim_pattern = r"(ПРОСИМ\s+СУД:.*?тенге\.)"
    prosim_match = re.search(prosim_pattern, text, re.S | re.I)
    if prosim_match:
        result["prosim"] = prosim_match.group(1).strip()

    return result