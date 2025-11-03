from common.download import downloadByButtonLabel 
from browser.browser import Browser
import time

def run(browser: Browser, data)->bool:
    print('Скачиваем последний файл')
    downloadByButtonLabel(browser, "Скачать талон об отправке", data['dir'])
    
    print('Zakonchil последний файл')
    
