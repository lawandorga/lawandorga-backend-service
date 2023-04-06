import abc
from typing import Any, Optional

from messagebus.domain.event import Event


class MessageBusRepository(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def save_event(
        cls,
        event: Event,
        position: Optional[int],
    ) -> Event:
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def save_command(cls, command: Any, position: Optional[int]) -> Any:
        raise NotImplementedError()
