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

    def chunk_list(self, lst, n):
        k, m = divmod(len(lst), n)
        return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

    @abstractmethod
    def label(self) -> str:
        pass

    @abstractmethod
    def start(self):
        pass
