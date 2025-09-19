import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def uploadFile(browser, file_path: str, id_suffix: str):
    file_path = os.path.abspath(file_path)

    selector = f"div[id$='{id_suffix}'] input[type='file'], span[id$='{id_suffix}'] input[type='file']"

    file_input = browser.wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    )

    file_input.send_keys(file_path)

def uploadFiles(browser, files: list[str], id_suffix: str):
    abs_paths = [os.path.abspath(f) for f in files]

    files_str = "\n".join(abs_paths)
    selector = f"div[id$='{id_suffix}'] input[type='file'], span[id$='{id_suffix}'] input[type='file']"

    file_input = browser.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    file_input.send_keys(files_str)


def uploadAllFilesInDirectory(browser, directory, id_suffix):
    allowed_ext = (".doc", ".docx", ".pdf", ".jpeg", ".jpg")

    files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
        and f.lower() != "desktop.ini"
        and f.lower().endswith(allowed_ext)
    ]

    uploadFiles(browser, files, id_suffix)