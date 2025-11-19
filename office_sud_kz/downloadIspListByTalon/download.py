from browser.browser import Browser
from common.download import downloadByElement

def run(browser: Browser, data, links):
    for link in links:
        downloadByElement(browser, link, data['talon'])