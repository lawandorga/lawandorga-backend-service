import abc
from typing import Optional, TypeVar

from messagebus.domain.message import Message

M = TypeVar("M", bound=Message)


class MessageBusRepository(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def save_message(
        cls,
        event: M,
        position: Optional[int],
    ) -> M:
        raise NotImplementedError()
