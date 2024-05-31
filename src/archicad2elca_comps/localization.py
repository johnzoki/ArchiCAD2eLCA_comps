"""
Reference:
    autor: Aaron Neugebauer
    date: 2024/05/31
"""
from archicad2elca_comps.config import languages

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Loc(metaclass=Singleton):
    def __init__(self, lang: str = "GERMAN"):
        self._local: dict[str, dict[str, str]] = languages
        self.set_lang(lang)

    def set_lang(self, lang: str):
        self._language = lang
        for key, value in self._local[lang].items():
            self.__setattr__(key, value)