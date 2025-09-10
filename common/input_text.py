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

def textByLabel(browser: Browser, label_text: str, text: str):
    label_xpath = f'//label[contains(normalize-space(.), "{label_text}")]'
    label_el = browser.wait.until(EC.presence_of_element_located((By.XPATH, label_xpath)))

    for_attr = label_el.get_attribute("for")
    if not for_attr:
        raise Exception(f'Label "{label_text}" has no "for" attribute')

    input_xpath = f'//*[@id="{for_attr}"]'
    input_el = browser.wait.until(EC.presence_of_element_located((By.XPATH, input_xpath)))

    try:
        input_el.clear()
        input_el.send_keys(text)
    except Exception:
        # Fallback: force-set value with JS if normal typing fails
        browser.driver.execute_script("""
            arguments[0].setAttribute('value', arguments[1]);
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, input_el, text)

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
        return text_el.get_attribute("value") == expected_text
    except:
        return False

def textModalByRow(browser: Browser, div_id: str, row_index: int, text: str):
    """
    Fill text into the <input> or <textarea> inside the given row number (1-based)
    inside a specific modal/container <div>.
    Example: div_id="jurModalDialog", row_index=4 → <div id="jurModalDialog">...<tbody><tr>[4]</tr>
    """
    xpath = f"(//div[@id='{div_id}']//tbody/tr)[{row_index}]//input | (//div[@id='{div_id}']//tbody/tr)[{row_index}]//textarea"
    el = browser.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

    try:
        el.clear()
        el.send_keys(text)
    except Exception as e:
        browser.driver.execute_script("""
            arguments[0].setAttribute('value', arguments[1]);
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, el, text)