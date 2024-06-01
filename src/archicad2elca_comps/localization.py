"""
Reference:
    autor: Aaron Neugebauer
    date: 2024/05/31
"""

from archicad2elca_comps.config import languages


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class Lang(Singleton):
    def __init__(self, lang: str = "GERMAN"):
        self._local: dict[str, dict[str, str]] = languages
        self.set_lang(lang)

    def set_lang(self, lang: str):
        self._language = lang
        try:
            for key, value in self._local[lang].items():
                self.__setattr__(key, value)
        except KeyError:
            raise RuntimeError(
                f"Language '{lang}' is not defined in 'config.py'!"
            ) from None
