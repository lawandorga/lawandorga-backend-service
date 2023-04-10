import abc
from typing import Optional, Type

from django.conf import settings
from django.utils.module_loading import import_string


class SingletonRepository(abc.ABC):
    IDENTIFIER: str
    SETTING: str
    _instance: Optional["SingletonRepository"] = None

    def __new__(cls, *args, **kwargs):
        if len(cls.mro()) == 5:
            return super().__new__(cls)

        module = import_string(settings.__getattr__(cls.SETTING))

        if cls._instance is None or not isinstance(cls._instance, module):
            cls._instance = module.__new__(module, *args, **kwargs)

        assert isinstance(cls._instance, module)

        return cls._instance
