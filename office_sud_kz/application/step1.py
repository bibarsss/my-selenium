from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from common.input_select import selectByLabel, selectByLabelOnModal, isSelectedByLabel, isSelectedByLabelOnModal
from common.button import clickByValue, clickByText, clickButtonByRow, clickFooterButtonByValue
from common.input_check import checkboxByTextValue
from common.input_text import textByLabel 
from browser.browser import Browser
from common.podsudnost import getPodsudnostValue
from common.read_pdf import read
from pathlib import Path
from common.input_upload import uploadFile
import os
import re

def run(browser: Browser, data)->bool:
    while not isSelectedByLabel(browser, "Вид документа по делу", "PETITION"):
        selectByLabel(browser, "Вид документа по делу", "PETITION")
        browser.wait_for_loader_done()

    file_path = data['file_path']
    if not Path(file_path).exists():
        raise Exception("File not found! " + file_path)

    parsed = parse(read(os.path.abspath(file_path)))
    textByLabel(browser, 'Текст ходатайства', parsed)

    uploadFile(browser, file_path, "selectRequiredScanUploader")
    browser.wait_for_loader_done()

    textByLabel(browser, 'Адрес', data['address'])
    textByLabel(browser, 'Номер дела', data['nomer_dela'])
    textByLabel(browser, 'Истцы по делу', data['istcy_po_delu'])
    textByLabel(browser, 'Ответчики по делу', data['otvet4ik_po_delu'])
    
    podsudnost = getPodsudnostValue(data['podsudnost'])
    sudValue = podsudnost['sudValue']
    sudName = podsudnost['sudName']
    oblastValue = podsudnost['oblastValue']

    if not bool(sudValue) or not bool(sudName):
        raise Exception('Подсудность в справочнике не найдены')
    
    while not isSelectedByLabel(browser, "Область (столица, город республиканского значения)", oblastValue) or not isSelectedByLabel(browser, "Судебный орган", sudValue):
        selectByLabel(browser, "Область (столица, город республиканского значения)", oblastValue)
        browser.wait_for_loader_done()
        if not browser.htmlHasText(sudName):
            continue
        browser.wait_for_loader_done()
        selectByLabel(browser, "Судебный орган", sudValue)
        browser.wait_for_loader_done()
        
    while not browser.htmlHasText("Предпросмотр электронного бланка"):
        clickByText(browser, 'a' ,'Далее')
        browser.wait_for_loader_done()

def parse(text):
    cleaned = text.strip()

    pattern = re.compile(
        r'ЗАЯВЛЕНИЕ\s*на выдачу исполнительного листа(.*?)\d{2}\.\d{2}\.\d{4}\s*г?\.?',
        re.DOTALL | re.IGNORECASE
    )

    match = pattern.search(cleaned)
    if not match:
        return ""

    result = match.group(1).strip()
    result = re.sub(r'[ \t]+', ' ', result)
    result = re.sub(r'\s*\n\s*', '\n', result)

    return result