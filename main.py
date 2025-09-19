from browser.browser import Browser
from office_sud_kz.auth import auth
from office_sud_kz.isk.main import run as iskRun
from selenium.webdriver.support.ui import WebDriverWait
from office_sud_kz.auth import is_authorized
import time
import globals
from openpyxl import load_workbook


def main():
    # browser = Browser()
    # print('Заходим в "office.sud.kz"...')
    # browser.safe_get("https://office.sud.kz/")

    # print('Авторизация...')
    # try:
    #     auth(browser)
    # except Exception as e:
    #     print("Ошибка авторизации!", e)
    #     browser.driver.quit()
    #     return

    # if not is_authorized(browser):
    #     print("Не авторизован!")
    #     browser.driver.quit()
    #     return
    # print('Успешно!')
    
    a = 1

    



    # globals.globalData.clear()
    # globals.globalData['iin'] = globals.authData['iin']

    # try: 
    #     print("Иск 1")
    #     iskRun(browser)
    # except Exception as e:
    # # 502 Bad Gateway не решенный

    #     print('Ошибка: ', e)
    #     browser.driver.quit()
    #     return
    
    # input("Готово. Для выхода нажмите на Enter.")
    # browser.driver.quit()

if __name__ == "__main__":
    main()