from typing import Optional, Sequence, TypeVar

from messagebus.domain.message import DomainMessage, Message
from seedwork.repository import SingletonRepository

M = TypeVar("M", bound=Message)


class EventStore(SingletonRepository):
    SETTING = "MESSAGEBUS_EVENT_STORE"

    def append(self, messages: Sequence[Message], position: Optional[int] = None):
        raise NotImplementedError()

    def load(self, stream_name: str) -> list[DomainMessage]:
        raise NotImplementedError()
