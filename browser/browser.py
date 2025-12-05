from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import os
import platform

class Browser:
    def __init__(self, with_gui = False, download_dir = "downloads"):
        self.download_dir = os.path.join(os.getcwd(), download_dir)
        os.makedirs(self.download_dir, exist_ok=True)

        options = Options()
        options.page_load_strategy = "normal"

        prefs = {
                    "download.default_directory": self.download_dir,
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                }

        options.add_experimental_option("prefs", prefs)

        if not with_gui:
            options.add_argument("--headless=new")
            options.add_argument("--headless")       # Run without GUI
            options.add_argument("--disable-gpu")    # Recommended for headless
            options.add_argument("--disable-dev-shm-usage")  # Fixes some crashes

        system = platform.system()
        if system == "Windows":
            driver_path = os.path.join(os.getcwd(), "chromedriver.exe")  # put chromedriver.exe in your project folder
        elif system == "Darwin":  # macOS
            driver_path = "/opt/homebrew/bin/chromedriver"

        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 60)

    def main_office_sud_kz(self):
        self.safe_get("https://office.sud.kz/")

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

    def htmlHasText(self, text: str) -> bool:
        xpath = f'//*[contains(normalize-space(.), "{text.strip()}")]'
        try:
            WebDriverWait(self.driver, 0.1).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return True
        except Exception:
            return False

    def tagWithTextHasClass(self, tag: str, text: str, className: str):
        xpath = f'//{tag}[normalize-space()="{text}"]'
        try:
            el = self.driver.find_element(By.XPATH, xpath)
            classes = el.get_attribute("class") or ""
            return className in classes.split()
        except:
            return False
