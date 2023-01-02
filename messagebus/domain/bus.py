from logging import getLogger
from typing import Callable, Optional, Type

from messagebus.domain.event import Event
from messagebus.domain.repository import MessageBusRepository

logger = getLogger("messagebus")


class MessageBus:
    handlers: dict[str, set[Callable]] = {}
    repository: Type[MessageBusRepository]

    @classmethod
    def set_repository(cls, repository: Type[MessageBusRepository]):
        cls.repository = repository

    @classmethod
    def register_handler(cls, action: str, handler: Callable):
        if action not in cls.handlers:
            cls.handlers[action] = set()
        cls.handlers[action].add(handler)
        logger.info(f"Handler {handler.__name__} registered for action '{action}'.")

    @classmethod
    def handle(cls, message: Event):
        if message.name in cls.handlers:
            for handler in cls.handlers[message.name]:
                handler(message)

    @classmethod
    def save_event(cls, event: Event, position: Optional[int] = None) -> Event:
        return cls.repository.save_event(event, position)

    @classmethod
    def save_command(cls, *args, **kwargs):
        raise NotImplementedError()
