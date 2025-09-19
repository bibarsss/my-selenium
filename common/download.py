import os
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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
    resp = session.get(file_url, stream=True)
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
