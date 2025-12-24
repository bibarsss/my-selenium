from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from common.input_select import selectByLabel, selectByLabelOnModal, isSelectedByLabel, isSelectedByLabelOnModal
from common.button import clickByValue, clickByText, clickButtonByRow, clickFooterButtonByValue
from common.input_check import checkboxByTextValue
from common.input_text import textModalByRow
from browser.browser import Browser
from common.podsudnost import getPodsudnostValue
from globals import RETRY_COUNT

def run(browser: Browser, data)->bool:
    c = 0
    while not isSelectedByLabel(browser, "Вид производства по делу", "2") \
            or not isSelectedByLabel(browser, "Характер заявления", "1") \
            or not isSelectedByLabel(browser, "Категория дела", "22"):
        c += 1
        if c == RETRY_COUNT:
            raise Exception("Ошибка в step1")
        selectByLabel(browser, "Вид производства по делу", "2")
        browser.wait_for_loader_done()
        selectByLabel(browser, "Категория дела", "22")
        browser.wait_for_loader_done()
        selectByLabel(browser, "Характер заявления", "1")
        browser.wait_for_loader_done()

# представитель
    add_process_member(
        browser,
        div_id="fizModalDialog",
        open_selectors=[
            {"label": "Сторона процесса", "value": "5"},
        ],
        fields=[
            {"row": 3, "key": "iin", "click_after": True},
            {"row": 9, "key": "phone", "skip_verify": True},
        ],
        data=data,
    )

# истец
    add_process_member(
        browser,
        div_id="jurModalDialog",
        open_selectors=[
            {"label": "Тип лица", "value": "true"},
        ],
        fields=[
            {"row": 4, "key": "bin", "click_after": True},
            {"row": 7, "key": "address"},
            {"row": 8, "key": "detail"},
        ],
        data=data,
    )

# ответчик
    for row in data['rows']:
        add_process_member(
            browser,
            div_id="fizModalDialog",
            open_selectors=[
                {"label": "Сторона процесса", "value": "2"},
            ],
            fields=[
                {"row": 3, "key": "iin_otvet4ik", "click_after": True},
                {"row": 9, "key": "phone_otvet4ik", "skip_verify": True},
            ],
            data={'iin_otvet4ik': row['iin_otvet4ik'], 'phone_otvet4ik': row['phone_otvet4ik']},
        )

    podsudnost = getPodsudnostValue(data['rows'][0]['podsudnost'])
    sudValue = podsudnost['sudValue']
    sudName = podsudnost['sudName']
    oblastValue = podsudnost['oblastValue']

    if not bool(sudValue) or not bool(sudName):
        raise Exception('Подсудность в справочнике не найдены')

    c = 0
    while not isSelectedByLabel(browser, "Область (столица, город республиканского значения)", oblastValue) \
            or not isSelectedByLabel(browser, "Судебный орган", sudValue):
        selectByLabel(browser, "Область (столица, город республиканского значения)", oblastValue)
        c += 1
        if c == RETRY_COUNT:
            raise Exception("Ошибка в step1")
        browser.wait_for_loader_done()

        selectByLabel(browser, "Судебный орган", sudValue)
        browser.wait_for_loader_done()


    checkboxByTextValue(browser, "Дело упрощенного производства", True)
    browser.wait_for_loader_done()

    c = 0
    while not browser.htmlHasText("Информация об оплате"):
        c += 1
        if c == RETRY_COUNT:
            raise Exception("Ошибка в step1")
        clickByText(browser, 'a' ,'Далее')
        browser.wait_for_loader_done()

    return True

def isModalOpened(browser: Browser, modal_id: str) -> bool:
    try:
        modal = browser.driver.find_element(By.ID, modal_id)
        return "in" in modal.get_attribute("class").split()
    except:
        return False

def verifyModalRowValue(browser: Browser, div_id: str, row_index: int, expected: str) -> bool:
    xpath = f"(//div[@id='{div_id}']//tbody/tr)[{row_index}]//input | (//div[@id='{div_id}']//tbody/tr)[{row_index}]//textarea"
    el = browser.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    actual = el.get_attribute("value") or el.text
    is_ok = (actual.strip() == expected.strip())
    return is_ok

def add_process_member(
    browser,
    *,
    div_id: str,
    open_selectors: list,
    fields: list,
    data: dict,
):
    browser.refresh()

    # open select-side modal
    c = 0
    while not isModalOpened(browser, 'selectSideModalDialog'):
        c += 1
        if c == RETRY_COUNT:
            raise Exception("Ошибка в step1 (open select modal)")
        clickByText(browser, 'button', 'Добавить участника процесса')
        browser.wait_for_loader_done()

    browser.wait_for_loader_done()

    # open target modal (apply selectors)
    c = 0
    while not isModalOpened(browser, div_id):
        c += 1
        if c == RETRY_COUNT:
            raise Exception("Ошибка в step1 (open target modal)")

        for selector in open_selectors:
            cc = 0
            while not isSelectedByLabelOnModal(
                browser,
                selector["label"],
                selector["value"],
            ):
                cc += 1
                if cc == RETRY_COUNT:
                    raise Exception("Ошибка в step1 (select label)")
                selectByLabelOnModal(
                    browser,
                    selector["label"],
                    selector["value"],
                )
                browser.wait_for_loader_done()

        clickByValue(browser, "Далее")
        browser.wait_for_loader_done()

    # fill modal fields
    c = 0
    while not all(
        verifyModalRowValue(browser, div_id, f["row"], data[f["key"]])
        for f in fields
        if not f.get('skip_verify', False)
    ):
        c += 1
        if c == RETRY_COUNT:
            raise Exception("Ошибка in step1 (fill fields)")

        for f in fields:
            textModalByRow(browser, div_id, f["row"], data[f["key"]])
            browser.wait_for_loader_done()

            if f.get("click_after"):
                clickButtonByRow(browser, div_id, f["row"])
                browser.wait_for_loader_done()

    clickFooterButtonByValue(browser, div_id, "Сохранить")
    browser.wait_for_loader_done()
