from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from browser.browser import Browser
import re

def run(browser: Browser, data):
    sections = browser.driver.find_elements(
        By.XPATH,
        "//div[@class='my-cases-folders-item' and .//a[contains(normalize-space(.), 'Статусы')]]"
    )

    links1 = []
    if sections:
        section = sections[0]
        links1 = section.find_elements(
            By.XPATH, ".//a[contains(@href, 'noticeAttachDownload')]"
        )


    sections = browser.driver.find_elements(
        By.XPATH,
        "//div[@class='my-cases-folders-item' and .//a[contains(normalize-space(.), 'Динамика хода рассмотрения дела')]]"
    )

    links2 = []
    if sections:
        section = sections[0]
        links2 = section.find_elements(
            By.XPATH, ".//a[contains(@href, 'noticeAttachDownload')]"
        )

    links = links1 + links2
    if len(links) == 0:
        raise Exception('Ссылки не найдены')

    return links 


def get_result_data(items):
    for item in reversed(items):
        result = get_result(item['text']) 
        if result is not None:
            result_date = item['date']
            result_sud_name = get_result_sud_name(item['text']) 
            result_number = get_result_number(item['text'])
            return {
                'result': result,
                'result_date': result_date,
                'result_sud_name': result_sud_name,
                'result_number': result_number
            }

    return None
    

def get_result_sud_name(text):
    text = text.strip()

    match = re.search(r"Судья\s*[–-]\s*([А-ЯЁ][А-ЯЁ\-]+\s+[А-ЯЁ]\.\s*[А-ЯЁ]\.)", text)
    if match:
        return match.group(1).strip()

    return ""

def get_result_number(text):
    text = text.replace('\n', ' ')
    match = re.findall(r"№\s*([\d\-\/]+)", text)
    
    if len(match) != 0:
        for m in match:
            if '-' in m and '/' in m:
                return m

    return ''

def get_result(text):
    text = text.lower().strip()

    if 'решение' in text:
        return 'решение'
    elif 'медиации' in text:
        return 'медиация'
    elif 'упрощенного производства' in text:
        return 'упр'
    elif 'зарегистрировано' in text:
        return 'зарегистрировано'
    elif 'возвра' in text:
        return 'возврат'
    elif 'отклон' in text:
        return 'отклонено'
    elif 'иск отправлено' in text:
        return 'иск отправлено'
    else:
        return None