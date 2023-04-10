from typing import Optional, Sequence, TypeVar

from messagebus.domain.message import DomainMessage, Message
from seedwork.repository import SingletonRepository

M = TypeVar("M", bound=Message)


class EventStore(SingletonRepository):
    """
    The EventStore is responsible for storing and loading messages.
    While Events are supposed to be stored forever, Commands can be thrown away.
    """

    SETTING = "MESSAGEBUS_EVENT_STORE"

    def append(self, messages: Sequence[Message], position: Optional[int] = None):
        raise NotImplementedError()

    def load(self, stream_name: str) -> list[DomainMessage]:
        raise NotImplementedError()
