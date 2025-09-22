from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time

class Browser:
    def __init__(self):
        options = Options()
        options.add_argument("--headless")       # Run without GUI
        options.add_argument("--disable-gpu")    # Recommended for headless
        options.add_argument("--disable-dev-shm-usage")  # Fixes some crashes
        options.page_load_strategy = "normal"

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 60)

    def safe_get(self, url, timeout=5, retries=1):
        for attempt in range(retries + 1):
            self.driver.get(url)
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                return True 
            except TimeoutException:
                if attempt < retries:
                    self.driver.refresh()
                else:
                    return False
                
    def refresh(self):
        self.driver.refresh()

    def wait_for_loader_done(self, timeout=30):
        try:
            WebDriverWait(self.driver, timeout).until(lambda d: "d-none" in d.find_element(By.CSS_SELECTOR, "span.loader").get_attribute("class"))
        except TimeoutException:
            raise TimeoutException("Loader did not disappear within timeout")