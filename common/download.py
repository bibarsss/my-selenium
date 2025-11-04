import os
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
def downloadByLabel(browser, link_text: str, download_dir: str, filename: str = None) -> str:
    os.makedirs(download_dir, exist_ok=True)

    # wait until link is present
    link = browser.wait.until(
        EC.presence_of_element_located((By.LINK_TEXT, link_text))
    )
    file_url = link.get_attribute("href")

    # prepend domain if relative
    if file_url.startswith("/"):
        current = browser.driver.current_url
        domain = current.split("/")[0] + "//" + current.split("/")[2]
        file_url = domain + file_url

    # reuse cookies from Selenium
    session = requests.Session()
    for cookie in browser.driver.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'])

    # download file
    # resp = session.get(file_url, stream=True)
    resp = session.get(file_url, stream=True, verify=False)
    resp.raise_for_status()

    # decide filename
    if not filename:
        cd = resp.headers.get("Content-Disposition")
        if cd and "filename=" in cd:
            filename = cd.split("filename=")[1].strip('"')
        else:
            filename = os.path.basename(file_url.split("?")[0]) or "download.bin"

    filepath = os.path.join(download_dir, filename)

    with open(filepath, "wb") as f:
        for chunk in resp.iter_content(8192):
            f.write(chunk)

    return filepath

def downloadByButtonLabel(browser, button_value: str, download_dir: str, timeout: int = 30) -> str:
    os.makedirs(download_dir, exist_ok=True)

    # Find button by value
    button = WebDriverWait(browser.driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, f"//input[@type='submit' and @value='{button_value}']"))
    )

    # Track existing files before click
    existing_files = set(os.listdir(download_dir))

    # Click the button
    button.click()

    # Wait until a new file appears in the download directory
    # end_time = time.time() + timeout
    # while time.time() < end_time:
    #     current_files = set(os.listdir(download_dir))
    #     new_files = current_files - existing_files
    #     if new_files:
    #         # We found a new file downloaded
    #         filename = new_files.pop()
    #         return os.path.join(download_dir, filename)
    #     time.sleep(0.5)

    # raise TimeoutError(f"No new file appeared in '{download_dir}' within {timeout} seconds")