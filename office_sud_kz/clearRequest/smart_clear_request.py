from browser.browser import Browser
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import time

from common.button import clickByText

def run(browser: Browser):
    browser.wait_for_loader_done()

    while not browser.tagWithTextHasClass('a', 'Ожидает отправки', 'active'):
        browser.safe_get('https://office.sud.kz/form/cases/wait.xhtml')
        browser.wait_for_loader_done()
        time.sleep(2)

    last_index = 0
    repeat = False
    while True:
        rows = browser.driver.find_elements(By.XPATH, "//table[contains(@class,'oldstyle')]/tbody/tr[@class='hovered']")
        row_count = len(rows)
        row_deleted = False
        for i in range(row_count - 1, -1, -1):  # start from last row, down to first
            if last_index > i and repeat:
                continue

            to_delete = False
            row_xpath = f"(//table[contains(@class,'oldstyle')]/tbody/tr[@class='hovered'])[ {i + 1} ]"

            row_el = browser.wait.until(EC.element_to_be_clickable((By.XPATH, row_xpath)))

            try:
                row_el.click()
            except:
                browser.driver.execute_script("arguments[0].click();", row_el)

            browser.wait_for_loader_done()
            to_delete = not browser.htmlHasText("Предпросмотр электронного бланка")

            browser.driver.back()
            browser.wait_for_loader_done()

            if to_delete:
                last_index = i
                row_deleted = True
                clickDeleteAndConfirm(browser, i)

        if row_deleted:
            repeat = True
            continue

        if not nextPageButtonExists(browser):
            break

        last_index = 0
        repeat = False

        clickByText(browser, "a", "►")
        time.sleep(2)
        browser.refresh()

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

def nextPageButtonExists(browser: Browser) -> bool:
    try:
        browser.driver.find_element(By.XPATH, "//div[contains(@class,'list-pages')]//a[text()='►']")
        return True
    except Exception:
        return False
