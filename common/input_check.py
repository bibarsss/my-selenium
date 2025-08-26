from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from browser.browser import Browser


def checkboxByTextValue(browser: Browser, text_value: str, checked: bool = True):
    xpath = f'//input[@type="text" and @value="{text_value}"]/preceding-sibling::span/input[@type="checkbox"]'
    browser.wait.until(_toggleIsReady(browser, xpath))
    el = browser.driver.find_element(By.XPATH, xpath)
    if el.is_selected() != checked:
        el.click()

def radioByTextValue(browser: Browser, text_value: str):
    xpath = f'//input[@type="text" and @value="{text_value}"]/preceding-sibling::span/input[@type="radio"]'
    browser.wait.until(_toggleIsReady(browser, xpath))
    el = browser.driver.find_element(By.XPATH, xpath)
    if not el.is_selected():
        el.click()

def _toggleIsReady(browser: Browser, xpath: str):
    def _predicate(_):
        try:
            el = browser.driver.find_element(By.XPATH, xpath)
            return el.is_displayed() and el.is_enabled()
        except:
            return False
    return _predicate