import os
from selenium.webdriver.common.by import By

def uploadFile(browser, file_path: str, id: str):
    file_path = os.path.abspath(file_path)

    file_input = browser.driver.find_element(By.CSS_SELECTOR, "span[id$='" + id + "'] input[type='file']")

    file_input.send_keys(file_path)