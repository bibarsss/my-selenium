from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


class Browser:
    def __init__(self):
        options = Options()
        # options.add_argument("--headless")       # Run without GUI
        # options.add_argument("--disable-gpu")    # Recommended for headless
        # options.add_argument("--no-sandbox")     # Useful in Linux
        # options.add_argument("--disable-dev-shm-usage")  # Fixes some crashes

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 100)

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
                    print(f"[!] Page didn't load in {timeout}s, refreshing (attempt {attempt + 1})")
                    self.driver.refresh()
                else:
                    print(f"[!] Page failed to load after {retries + 1} attempts")
                    return False
    
    # def wait_for_page_load(self, timeout=10):
        # self.wait.until(lambda d: d.execute_script("return document.readyState") == "interactive")