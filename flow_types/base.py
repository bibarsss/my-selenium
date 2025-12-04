import sqlite3
from globals import Config
from abc import ABC, abstractmethod
from browser.browser import Browser

class Type(ABC):
    def __init__(self, cfg: Config = None):
        self.__cfg = cfg

    @property
    def cfg(self):
        return self.__cfg

    def browser(self):
        return Browser(bool(int(self.cfg.get('show_browser'))))

    @abstractmethod
    def label(self) -> str:
        pass

    @abstractmethod
    def start(self):
        pass
