import abc
from typing import Any, Optional
from uuid import UUID

from messagebus.domain.event import Event, RawEvent


class MessageBusRepository(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def save_event(cls, event: RawEvent, stream_name: str, aggregate_id: UUID, position: Optional[int]) -> Event:
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def save_command(cls, command: Any, position: Optional[int]) -> Any:
        raise NotImplementedError()
