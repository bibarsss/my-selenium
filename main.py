from browser.browser import Browser
from office_sud_kz.auth import auth
from office_sud_kz.isk.main import run as iskRun
from selenium.webdriver.support.ui import WebDriverWait

import time

def main():
    print('Zapusk...')
    browser = Browser()
    
    print('auth...')
    is_auth = auth(browser)
    if not is_auth:
        print("Not authorized")
        return
    
    print('isk...')
    iskRun(browser)

    input("Job is done. Press Enter to close...")
    browser.driver.quit()

if __name__ == "__main__":
    main()