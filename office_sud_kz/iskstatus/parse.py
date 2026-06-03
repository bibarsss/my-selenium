from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from browser.browser import Browser
import re

def run(browser: Browser, data):
    items = get_dynamic_review_items(browser)
    parsed_data = get_result_data(items, browser)
    if parsed_data is None:
        raise Exception('Динамика хода рассмотрения дела ПУСТАЯ!')

    return parsed_data

def get_dynamic_review_items(browser):
    result = []

    try:
        section = browser.driver.find_element(
            By.XPATH,
            "//div[@class='my-cases-folders-item' and .//a[contains(normalize-space(.), 'Динамика хода рассмотрения дела')]]"
        )

        items = section.find_elements(By.CSS_SELECTOR, "div.panel-body div.well.well-sm")

        for item in items:
            try:
                date_el = item.find_element(By.XPATH, ".//p[contains(text(), '.') and contains(text(), ':')]")
                date_text = date_el.text.strip()

                text_el = item.find_element(By.XPATH, ".//div[contains(@style, 'margin-left')]")
                text = text_el.text.strip()

                result.append({"date": date_text, "text": text})
            except NoSuchElementException:
                continue

    except NoSuchElementException:
        pass

    return result

def get_result_data(items, browser):
    result_otvet4ik_iin, result_otvet4ik_name = get_otvetchik_data(browser)
    result_oblast, result_sud = get_oblast_and_sud(browser)
    result_title = get_title(browser)
    for item in reversed(items):
        result = get_result(item['text'])
        if result is not None:
            result_date = item['date']
            result_sud_name = get_result_sud_name(item['text'])
            result_number = get_result_number(item['text'])
            # result_text = ''
            # if result in ['возврат', 'отклонено']:
            #     result_text = item['text']
            result_text = item['text']

            return {
                'result': result,
                'result_date': result_date,
                'result_sud_name': result_sud_name,
                'result_number': result_number,
                'result_text': result_text,
                'result_otvet4ik_iin': result_otvet4ik_iin,
                'result_otvet4ik_name': result_otvet4ik_name,
                'result_oblast': result_oblast,
                'result_sud': result_sud,
                'result_title': result_title,
            }

    if len(items) == 0:
        return None

    return {
        'result': 'неизвестно',
        'result_date': item['date'],
        'result_sud_name': '',
        'result_number': '',
        'result_text': item['text'],
        'result_otvet4ik_iin': result_otvet4ik_iin,
        'result_otvet4ik_name': result_otvet4ik_name,
        'result_oblast': result_oblast,
        'result_sud': result_sud,
        'result_title': result_title,
    }

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
    elif 'вынесено судебный приказ' in text:
        return 'вынесено СП'
    elif 'медиации' in text:
        return 'медиация'
    elif 'упрощенного производства' in text:
        return 'упр'
    elif 'возвра' in text:
        return 'возврат'
    elif 'отклон' in text:
        return 'отклонено'
    elif 'зарегистрировано' in text:
        return 'зарегистрировано'
    elif 'иск отправлено' in text:
        return 'иск отправлено'
    elif 'заявление успешно отправлено' in text:
        return 'заявление отправлено'
    else:
        return None

def get_otvetchik_data(browser):
    try:
        fieldset = browser.driver.find_element(
            By.XPATH,
            "//fieldset[.//div[contains(@class,'fieldset-legend') and contains(., 'Стороны процесса')]]"
        )

        rows = fieldset.find_elements(By.CSS_SELECTOR, "div.panel-body div.row")

        for row in rows:
            try:
                role = row.find_element(
                    By.XPATH,
                    ".//div[label[contains(.,'Сторона процесса')]]/p"
                ).text.strip().lower()

                if role not in ["ответчик", "должник"]:
                    continue

                iin = row.find_element(
                    By.XPATH,
                    ".//div[label[contains(.,'ИИН/БИН')]]/p"
                ).text.strip()

                name = row.find_element(
                    By.XPATH,
                    ".//div[label[contains(.,'ФИО/Наименование')]]/p"
                ).text.strip()

                return iin, name

            except NoSuchElementException:
                continue

    except NoSuchElementException:
        pass

    return '', ''

def get_oblast_and_sud(browser):
    oblast = browser.driver.find_element(
            By.XPATH,
            "//label[contains(text(),'Область')]/following::input[1]"
        ).get_attribute("value")

    sud = browser.driver.find_element(
        By.XPATH,
        "//label[contains(text(),'Судебный орган')]/following::input[1]"
    ).get_attribute("value")

    return oblast, sud

def get_title(browser):
    try:
        title_el = browser.driver.find_element(
            By.CSS_SELECTOR,
            "span.tab__inner-title"
        )
        full_text = title_el.text.strip()

        parts = full_text.split('>')
        if len(parts) >= 3:
            return parts[-1].strip()

        return ''
    except NoSuchElementException:
        return ''
