from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from browser.browser import Browser

def clickByText(browser: Browser, tag: str, text: str):
    xpath = f'//{tag}[contains(text(), "{text}")]'
    _clickByXpath(browser, xpath)

def clickByValue(browser: Browser, value):
    xpath = '//input[@value="' + value +'"]'
    _clickByXpath(browser, xpath)

def clickByIndex(browser: Browser, selector: str, index: int):
    browser.wait.until(_elementsAreReady(browser, selector, index))
    elements = browser.driver.find_elements(By.CSS_SELECTOR, selector)
    elements[index].click()

def _clickByXpath(browser: Browser, xpath: str):
    browser.wait.until(_clickIsReady(browser, xpath))
    el = browser.driver.find_element(By.XPATH, xpath)
    el.click()

def _clickIsReady(browser: Browser, xpath: str):
    def _predicate(_):
        try:
            el = browser.driver.find_element(By.XPATH, xpath)
            return el.is_displayed() and (el.is_enabled() or el.get_attribute("onclick"))
        except:
            return False
    return _predicate

def _elementsAreReady(browser: Browser, selector: str, index: int):
    def _predicate(_):
        try:
            elements = browser.driver.find_elements(By.CSS_SELECTOR, selector)
            if len(elements) > index:
                el = elements[index]
                return el.is_displayed() and el.is_enabled()
            return False
        except:
            return False
    return _predicate