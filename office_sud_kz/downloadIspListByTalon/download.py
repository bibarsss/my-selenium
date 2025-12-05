import os
import time
from browser.browser import Browser
from common.download import downloadByElement

def run(browser: Browser, data, file_links):
    download_dir = os.path.abspath("downloads_sk_talon")
    os.makedirs(download_dir, exist_ok=True)

    for link in file_links:
        # filename = link.text.strip().replace("/", "_").replace("\\", "_")
        # print(f"Downloading: {filename}")
        browser.driver.execute_script("arguments[0].scrollIntoView(true);", link)
        link.click()
