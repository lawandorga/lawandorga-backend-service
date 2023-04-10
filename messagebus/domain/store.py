import abc
from typing import Optional, Sequence, TypeVar

from django.conf import settings
from django.utils.module_loading import import_string

from messagebus.domain.message import DomainMessage, Message

M = TypeVar("M", bound=Message)


class EventStore(abc.ABC):
    SETTING = "MESSAGEBUS_EVENT_STORE"

    def __new__(cls, *args, **kwargs):
        if not cls == EventStore:
            return super().__new__(cls)

        module = import_string(settings.__getattr__(cls.SETTING))

        if cls._instance is None or not isinstance(cls._instance, module):
            cls._instance = module.__new__(module, *args, **kwargs)

        assert isinstance(cls._instance, EventStore)

        return cls._instance

    def append(self, messages: Sequence[Message], position: Optional[int] = None):
        raise NotImplementedError()

    def load(self, stream_name: str) -> list[DomainMessage]:
        raise NotImplementedError()
