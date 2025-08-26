from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from browser.browser import Browser

selectFirst = ["Судебный орган"]

def selectByLabel(browser: Browser, label, value):
    xpath = '//label[normalize-space()="' + label + '"]/following-sibling::select'
    if label in selectFirst:
        xpath = '//label[normalize-space()="' + label + '"]/following::select[1]'
    _selectByXpath(browser, xpath, value)

def selectByLabelOnModal(browser: Browser, label, value):
    xpath = f'//label[normalize-space()="{label}"]/parent::td/following-sibling::td/select'
    _selectByXpath(browser, xpath, value)
    
def _selectByXpath(browser: Browser, xpath, value):
    browser.wait.until(_hasOptionByXpath(xpath, value))
    toSelect = browser.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    Select(toSelect).select_by_value(value)

def _hasOptionByXpath(xpath, value):
    """Return a callable that checks if a <select> has an <option> with given value."""
    def _predicate(driver):
        try:
            # always re-find the select and its options fresh
            select = driver.find_element(By.XPATH, xpath)
            options = select.find_elements(By.TAG_NAME, "option")
            return any(o.get_attribute("value") == value for o in options)
        except Exception as e:
            return False
    return _predicate

def isSelectedByLabel(browser: Browser, label, value):
    xpath = f'//label[normalize-space()="{label}"]/following-sibling::select'
    if label in selectFirst:
        xpath = '//label[normalize-space()="' + label + '"]/following::select[1]'
    return _isSelectedByXpath(browser, xpath, value)

def isSelectedByLabelOnModal(browser: Browser, label, value):
    xpath = f'//label[normalize-space()="{label}"]/parent::td/following-sibling::td/select'
    return _isSelectedByXpath(browser, xpath, value)

def _isSelectedByXpath(browser: Browser, xpath: str, value: str) -> bool:
    try:
        select_element = WebDriverWait(browser.driver, 0.5).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        current_value = Select(select_element).first_selected_option.get_attribute("value")
        return current_value == value
    except:
        return False