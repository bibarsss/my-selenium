import threading
import time
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def safe_get(driver, url, timeout=5, retries=1):
    for attempt in range(retries + 1):
        driver.get(url)
        try:
            # Replace with a more specific element if possible
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            return True  # Page loaded successfully
        except TimeoutException:
            if attempt < retries:
                driver.refresh()
            else:
                return False