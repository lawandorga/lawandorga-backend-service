import abc
from typing import Optional

from django.conf import settings
from django.utils.module_loading import import_string


class SingletonRepository(abc.ABC):
    IDENTIFIER: str
    SETTING: str
    _instance: Optional["SingletonRepository"] = None

    @classmethod
    def get_setting(cls) -> str:
        return settings.__getattr__(cls.SETTING)

    @classmethod
    def get_module(cls) -> type:
        return import_string(cls.get_setting())

    def __new__(cls, *args, **kwargs):
        if isinstance(cls._instance, cls.mro()[0]):
            return cls._instance

        if cls._instance is None and len(cls.mro()) == 5:
            # this might look weird, because why 5?
            # the reason is we got the following resolution order:
            # InMemoryAggregateRespository -> AggreagateRepository -> SingletonRepository -> abc.ABC -> object
            # in case the number is 5 we are already in the correct class
            # otherwise we need to check the settings to get the correct class
            # because the AggregateRepository is supposed to be interface like
            # and with import string we get the correct settings class
            # or it is also possible to use a implemented class directly
            # like InMemoryAggregateRepository() instead of AggregateRepository()
            cls._instance = super().__new__(cls)
            return cls._instance

        module = cls.get_module()
        if not isinstance(cls._instance, module):
            cls._instance = None
            cls._instance = module.__new__(module, *args, **kwargs)

        assert isinstance(cls._instance, module)

        return cls._instance
