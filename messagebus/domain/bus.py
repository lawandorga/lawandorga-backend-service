from typing import Callable, Optional, Type

from messagebus.domain.event import Event
from messagebus.domain.repository import MessageBusRepository


class MessageBus:
    handler: dict[str, set[Callable]] = {}
    repository: Type[MessageBusRepository]

    @classmethod
    def set_repository(cls, repository: Type[MessageBusRepository]):
        cls.repository = repository

    @classmethod
    def register_handler(cls, action: str, handler: Callable):
        if action not in cls.handler:
            cls.handler[action] = set()
        cls.handler[action].add(handler)

    @classmethod
    def handle(cls, message: Event):
        if message.name in cls.handler:
            for h in cls.handler[message.name]:
                h(message)

    @classmethod
    def save_event(cls, event: Event, position: Optional[int] = None) -> Event:
        return cls.repository.save_event(event, position)

    @classmethod
    def save_command(cls, *args, **kwargs):
        raise NotImplementedError()
