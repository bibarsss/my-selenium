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
                print(f"[!] Page didn't load in {timeout}s, refreshing (attempt {attempt + 1})")
                driver.refresh()
            else:
                print(f"[!] Page failed to load after {retries + 1} attempts")
                return False

# def load_url(driver, url, done_flag):
#     try:
#         driver.get(url)
#         done_flag.append(True)
#     except Exception as e:
#         print(f"❌ Exception during driver.get: {e}")

# def safe_get(driver, url, timeout=10, max_retries=3):
#     for attempt in range(1, max_retries + 1):
#         print(f"[Attempt {attempt}] Loading {url}")
#         done_flag = []
#         thread = threading.Thread(target=load_url, args=(driver, url, done_flag))
#         thread.start()
#         thread.join(timeout)

#         if not done_flag:
#             print("⏱️ Page load stuck. Stopping and refreshing...")
#             try:
#                 driver.execute_script("window.stop();")  # force stop load
#             except Exception as e:
#                 print("⚠️ window.stop() failed:", e)

#             driver.refresh()
#             time.sleep(2)
#             continue

#         print("✅ Page loaded successfully.")
#         return True

#     print("❌ All retries failed.")
#     return False
    


# def safe_click(driver, button_locator, max_retries=3, wait_timeout=10):
#     """
#     Clicks a button that submits a form or triggers a POST request.
#     Refreshes the page if it gets stuck or fails.
#     """
#     from selenium.webdriver.support.ui import WebDriverWait
#     from selenium.webdriver.support import expected_conditions as EC

#     for attempt in range(1, max_retries + 1):
#         print(f"[Attempt {attempt}] Clicking submit...")

#         try:
#             WebDriverWait(driver, 5).until(EC.element_to_be_clickable(button_locator)).click()

#             if not wait_for_page_load(driver, timeout=wait_timeout):
#                 print("→ Page stuck loading. Refreshing...")
#                 driver.refresh()
#                 continue

#             if is_http_internal_error(driver):
#                 print("→ HTTP 500 detected. Refreshing...")
#                 driver.refresh()
#                 continue

#             print("✅ Submission successful.")
#             return True

#         except Exception as e:
#             print(f"⚠️ Exception on click: {e}")
#             driver.refresh()

#     print("❌ All attempts failed.")
#     return False

# def safe_get(driver, url, max_retries=3, wait_timeout=4):
#     for attempt in range(1, max_retries + 1):
#         print(f"[Attempt {attempt}] Navigating to {url}")
#         try:
#             driver.get(url)

#             if not wait_for_page_load(driver, timeout=wait_timeout):
#                 print("→ Page is stuck. Refreshing...")
#                 driver.refresh()
#                 continue

#             if is_http_internal_error(driver):
#                 print("→ HTTP 500 detected. Refreshing...")
#                 driver.refresh()
#                 continue

#             print("✅ Page loaded successfully.")
#             return True

#         except Exception as e:
#             print(f"⚠️ Exception during driver.get: {e}")
#             driver.refresh()

#     print("❌ All retries failed.")
#     return False

# def wait_for_page_load(driver, timeout=10):
#     import time
#     end_time = time.time() + timeout
#     while time.time() < end_time:
#         try:
#             state = driver.execute_script("return document.readyState")
#             if state == "complete":
#                 return True
#         except:
#             pass
#         time.sleep(0.5)
#     return False

# def is_http_internal_error(driver):
#     body = driver.page_source.lower()
#     return "internal server error" in body or "ошибка сервера" in body