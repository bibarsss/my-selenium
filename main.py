from browser.browser import Browser
from office_sud_kz.auth import auth
from office_sud_kz.isk.main import run as iskRun
from selenium.webdriver.support.ui import WebDriverWait
from office_sud_kz.auth import is_authorized
import os
import globals
from openpyxl import load_workbook
import unicodedata
from pathlib import Path

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


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
    
    print("Открываем файл sud.xlsx...")
    file_path = "sud.xlsx"
    wb = load_workbook(file_path)
    sheet = wb.active

    # iin = ''
    iin = globals.authData['iin']
    bin = "220440007472"
    address = "Алматинская область, Илийский р-н, с.о. Асқар Тоқпанов,с. Асқар Тоқпанов, ул. Қ.Байқадамқызы, д. 71, кв. 2"
    detail = "ИИК: KZ55601A861010717701 Банк: в АО «Народный банк Казахстана» БИК: HSBKKZKX"

    for i, row in enumerate(sheet.iter_rows(min_row=2, values_only=False), start=2):
        number = str(row[0].value)
        isk_file = str(row[1].value) + ".pdf"
        dir = None

        print("Строка " + str(i) + " -> " + number)
        if len(row) > 21 and str(row[20].value) == 'success':
            print("[Пропуск] Уже успешно!")
            continue

        for path in Path(".").rglob("*"):
            if unicodedata.normalize("NFC", path.name) == isk_file:
                dir = path.parent
                break

        if not dir:
            print("[Пропуск] Папка с иском не найдена!")

            col21_val = sheet.cell(row=i, column=21).value
            col22_val = sheet.cell(row=i, column=22).value

            if col21_val is None and col22_val is None:
                sheet.cell(row=i, column=21, value="error")
                sheet.cell(row=i, column=22, value="-")
                wb.save(file_path)

            continue

        sheet.cell(row=i, column=21, value="process")
        sheet.cell(row=i, column=22, value=str(dir))

        globals.globalData = {
            "iin": iin,
            "bin": bin,
            "address": address,
            "detail": detail,
            "podsudnost": str(row[3].value),
            "number": number,
            "iin_otvet4ik": str(row[6].value).zfill(12),
            "summaIska": str(row[11].value),
            "powlina": str(row[13].value),
            "dir": str(dir),
            "powlina_file_path": str(dir / "платежное поручение об оплате государственной пошлины.pdf"),
            "isk_file_path": str(dir / isk_file),
        }

        try:
            print(str(dir))
            iskRun(browser)
            sheet.cell(row=i, column=21, value="success")
            wb.save(file_path)

        except Exception as e:
            print("Ошибка:", e)
            sheet.cell(row=i, column=21, value="exception")
            wb.save(file_path)

    input("Готово. Для выхода нажмите на Enter.")
    browser.driver.quit()

if __name__ == "__main__":
    main()