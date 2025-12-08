from selenium.webdriver.common.by import By
from browser.browser import Browser

def run(browser: Browser, data):
    try:
        dinamika = browser.driver.find_element(
                By.XPATH,
                "//div[@class='my-cases-folders-item' and .//a[contains(normalize-space(.), 'Динамика хода рассмотрения дела')]]"
            )

        dinamika_links = dinamika.find_elements(By.TAG_NAME, "a")
    except Exception:
        dinamika_links = []

    try:
        statuses = browser.driver.find_element(
                By.XPATH,
                "//div[@class='my-cases-folders-item' and .//a[contains(normalize-space(.), 'Статусы')]]"
            )

        statuses_links = statuses.find_elements(By.TAG_NAME, "a")
    except Exception:
        statuses_links = []

    all_links = dinamika_links + statuses_links

    file_links = [
        link for link in all_links
        if "noticeAttachDownload" in link.get_attribute("href")
    ]

    print(f"[Worker {data['worker_id']}] Found {len(file_links)} files to download.")
    return file_links
