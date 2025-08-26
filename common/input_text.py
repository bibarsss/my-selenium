from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from browser.browser import Browser

def textByPlaceholder(browser: Browser, placeholder: str, text: str):
    xpath = f'//input[@placeholder="{placeholder}" or @placeholder="{placeholder} "] | //textarea[@placeholder="{placeholder}" or @placeholder="{placeholder} "]'
    _textByXpath(browser, xpath, text)

def textIsSetByPlaceholder(browser: Browser, placeholder: str, expected_text: str) -> bool:
    xpath = f'//input[@placeholder="{placeholder}" or @placeholder="{placeholder} "] | //textarea[@placeholder="{placeholder}" or @placeholder="{placeholder} "]'
    return _textIsSetByXpath(browser, xpath, expected_text)

def _textByXpath(browser: Browser, xpath: str, text: str):
    browser.wait.until(_textIsReady(browser, xpath))
    text_el = browser.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    text_el.clear()
    text_el.send_keys(text)

def _textIsReady(browser: Browser, xpath: str):
    def _predicate(_):
        try:
            el = browser.driver.find_element(By.XPATH, xpath)
            return el.is_displayed() and el.is_enabled()
        except:
            return False
    return _predicate

def _textIsSetByXpath(browser: Browser, xpath: str, expected_text: str) -> bool:
    try:
        browser.wait.until(_textIsReady(browser, xpath))
        text_el = browser.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        # print what was found
        print(f"[textByLabel] Found element for label '{label_text}':")
        print(text_el.get_attribute("outerHTML"))
        return text_el.get_attribute("value") == expected_text
    except:
        return False
    

def textByLabel(browser: Browser, label_text: str, text: str):
    xpath = f'//label[normalize-space()="{label_text}"]/parent::td/following-sibling::td//input | ' \
            f'//label[normalize-space()="{label_text}"]/parent::td/following-sibling::td//textarea | ' 
    _textByXpath(browser, xpath, text)


def textIsSetByLabel(browser: Browser, label_text: str, expected_text: str) -> bool:
    xpath = f'//label[normalize-space()="{label_text}"]/parent::td/following-sibling::td//input | ' \
            f'//label[normalize-space()="{label_text}"]/parent::td/following-sibling::td//textarea | ' 
    return _textIsSetByXpath(browser, xpath, expected_text)