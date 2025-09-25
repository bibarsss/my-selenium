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
    def _element_is_ready(_):
        try:
            elements = browser.driver.find_elements(By.CSS_SELECTOR, selector)
            if len(elements) > index:
                el = elements[index]
                return el.is_displayed() and el.is_enabled()
            return False
        except:
            return False

    browser.wait.until(_element_is_ready)
    elements = browser.driver.find_elements(By.CSS_SELECTOR, selector)
    el = elements[index]

    try:
        el.click()
    except Exception:
        browser.driver.execute_script("arguments[0].click();", el)


def clickButtonByRow(browser: Browser, div_id: str, row_index: int):
    xpath = f"(//div[@id='{div_id}']//tbody/tr)[{row_index}]//button | (//div[@id='{div_id}']//tbody/tr)[{row_index}]//span[contains(@class,'input-group-addon')] | (//div[@id='{div_id}']//tbody/tr)[{row_index}]//a"
    el = browser.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

    try:
        el.click()
    except Exception as e:
        browser.driver.execute_script("arguments[0].click();", el)

def clickFooterButtonByValue(browser: Browser, div_id: str, value: str):
    xpath = f"//div[@id='{div_id}']//div[contains(@class,'modal-footer')]//input[@value='{value}']"
    browser.wait.until(_clickIsReady(browser, xpath))
    el = browser.driver.find_element(By.XPATH, xpath)

    try:
        el.click()
    except Exception as e:
        browser.driver.execute_script("arguments[0].click();", el)

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