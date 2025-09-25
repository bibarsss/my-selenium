from browser.browser import Browser
from office_sud_kz.auth import auth
from office_sud_kz.isk.main import run as iskRun
from selenium.webdriver.support.ui import WebDriverWait
from office_sud_kz.auth import is_authorized
import globals
from openpyxl import load_workbook
import unicodedata
from pathlib import Path

import sys, io

sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer, 
    encoding="utf-8", 
    line_buffering=True
)

def main():
    browser = Browser()
    print('Заходим в "office.sud.kz"...')
    browser.safe_get("https://office.sud.kz/")

    print('Авторизация...')
    try:
        auth(browser)
    except Exception as e:
        print("Ошибка авторизации!", e)
        browser.driver.quit()
        return

    if not is_authorized(browser):
        print("Не авторизован!")
        browser.driver.quit()
        return
    print('Успешно!')
   
    print("Открываем файл " + globals.cfg['file'] + "...")
    file_path = globals.cfg['file']
    wb = load_workbook(file_path)
    sheet = wb.active

    for i, row in enumerate(sheet.iter_rows(min_row=2, values_only=False), start=2):
        if i % 5 == 0: 
            browser.refresh()

        number = str(row[globals.index('isk_excel_number')].value)
        isk_file = str(row[globals.index('isk_excel_file_name')].value) + ".pdf"
        dir = None

        print("Строка " + str(i) + " -> " + number)
        if len(row) > 21 and str(row[22].value) == 'success':
            print("[Пропуск] Уже успешно!")
            continue

        for path in Path(".").rglob("*.pdf"):
            if number in unicodedata.normalize("NFC", path.name):
                dir = path.parent
                break
        
        if not dir:
            print("[Пропуск] Папка с иском на договор [" + number + "] не найдена!")

            col21_val = sheet.cell(row=i, column=23).value
            col22_val = sheet.cell(row=i, column=24).value

            if col21_val is None and col22_val is None:
                sheet.cell(row=i, column=23, value="error")
                sheet.cell(row=i, column=24, value="-")
                wb.save(file_path)

            continue

        sheet.cell(row=i, column=23, value="process")
        sheet.cell(row=i, column=24, value=str(dir))

        globals.globalData = {
            "iin": globals.cfg['iin'],
            "bin": globals.cfg['bin'],
            "phone": globals.cfg['phone'],
            "phone_otvet4ik": str(row[globals.index("isk_excel_phone_otvet4ik")].value),
            "address": globals.cfg['address'],
            "detail": globals.cfg['detail'],
            "podsudnost": str(row[globals.index('isk_excel_podsudnost')].value),
            "number": number,
            "iin_otvet4ik": str(row[globals.index('isk_excel_iin_otvet4ik')].value).zfill(12),
            "summaIska": str(row[globals.index('isk_excel_summa_iska')].value),
            "powlina": str(row[globals.index('isk_excel_powlina')].value),
            "dir": str(dir),
            "powlina_file_path": str(dir / globals.cfg['isk_powlina_file_name']),
            "isk_file_path": str(dir / globals.cfg['isk_file_name']),
            "isk_file_realpath": str(dir / isk_file),
        }

        try:
            print(dir)
            iskRun(browser)
            sheet.cell(row=i, column=23, value="success")
            wb.save(file_path)

        except Exception as e:
            print("Ошибка:", e)
            sheet.cell(row=i, column=23, value="exception")
            wb.save(file_path)

    input("Готово. Для выхода нажмите на Enter.")
    browser.driver.quit()

if __name__ == "__main__":
    main()