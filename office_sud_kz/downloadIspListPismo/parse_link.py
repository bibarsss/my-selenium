import re
from browser.browser import Browser
from selenium.webdriver.common.by import By

def run(browser: Browser, number):
    section = browser.driver.find_element(
        By.XPATH,
        "//fieldset[.//legend//div[normalize-space()='Файлы']]"
    )

    links = section.find_elements(
        By.XPATH, ".//a[contains(@href, 'attachDownload')]"
    )

    files = []
    for link in links:
        files.append({
            "file_name": sanitize(number + '_' + link.text),
            "url": link.get_attribute("href")
        })

    return files

def sanitize(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '', name.strip())
