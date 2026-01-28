from browser.browser import Browser
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import time

def run(browser: Browser):
    browser.wait_for_loader_done()

    while not browser.tagWithTextHasClass('a', 'Ожидает отправки', 'active'):
        browser.safe_get('https://office.sud.kz/form/cases/wait.xhtml')
        browser.wait_for_loader_done()
        time.sleep(2)

    while True:
        print('while true')
        browser.refresh()
        delete_buttons = browser.driver.find_elements(By.XPATH, "//table[contains(@class,'oldstyle')]//a[img[contains(@src,'delete.png')]]")
        for _ in range(len(delete_buttons)):
            print('obwii')
            try:
                clickDeleteAndConfirm(browser, 0)  # alw
                browser.wait_for_loader_done()
            except:
                browser.wait_for_loader_done()
                continue

def clickDeleteAndConfirm(browser: Browser, row_index: int):
    browser.wait_for_loader_done()
    delete_xpath = f"(//table[contains(@class,'oldstyle')]//a[img[contains(@src,'delete.png')]])[{row_index + 1}]"

    browser.wait_for_loader_done()
    el = browser.wait.until(EC.element_to_be_clickable((By.XPATH, delete_xpath)))

    try:
        el.click()
    except:
        browser.driver.execute_script("arguments[0].click();", el)

    browser.wait_for_loader_done()

    confirm_button_xpath = "//div[@id='requestDeleteDialog']//input[@value='Да']"
    confirm_btn = browser.wait.until(EC.element_to_be_clickable((By.XPATH, confirm_button_xpath)))

    try:
        confirm_btn.click()
    except:
        browser.driver.execute_script("arguments[0].click();", confirm_btn)

    browser.wait_for_loader_done()

    browser.wait.until(lambda d: d.find_element(By.ID, "requestDeleteDialog").get_attribute("style") == "display: none;")

    browser.wait_for_loader_done()
