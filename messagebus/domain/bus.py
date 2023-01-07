from logging import getLogger
from typing import Callable, Optional, Type

from messagebus.domain.data import EventData
from messagebus.domain.event import Event, RawEvent
from messagebus.domain.repository import MessageBusRepository

logger = getLogger("messagebus")


class MessageBus:
    handlers: dict[Type[EventData], set[Callable]] = {}
    repository: Type[MessageBusRepository]
    event_models: dict[str, Type[EventData]] = {}

    @classmethod
    def register_event_model(cls, model_class: Type[EventData]):
        if model_class.get_name() in cls.event_models:
            raise ValueError("This event is already registered.")

        cls.event_models[model_class.get_name()] = model_class

    @classmethod
    def get_event_model(cls, name: str):
        if name not in cls.event_models:
            raise ValueError("Event data could not be found.")

        return cls.event_models[name]

    @classmethod
    def event(cls, model_class: Type[EventData]):
        cls.register_event_model(model_class)

        return model_class

    @classmethod
    def handler(
        cls, on: Type[EventData] | list[Type[EventData]]
    ) -> Callable[[Callable[[Event], None]], Callable[[Event], None]]:
        def wrapper(handler: Callable[[Event], None]) -> Callable[[Event], None]:
            when = on if isinstance(on, list) else [on]

            for name in when:
                cls.register_handler(name, handler)

            return handler

        return wrapper

    @classmethod
    def set_repository(cls, repository: Type[MessageBusRepository]):
        cls.repository = repository

    @classmethod
    def register_handler(cls, action: Type[EventData], handler: Callable):
        if isinstance(action, str):
            return

        if action.get_name() not in cls.handlers:
            cls.handlers[action.get_name()] = set()

        cls.handlers[action.get_name()].add(handler)

        logger.info(
            f"Handler {handler.__name__} registered for action '{action.get_name()}'."
        )

    @classmethod
    def handle(cls, message: RawEvent | Event):
        if message.name in cls.handlers:
            for handler in cls.handlers[message.name]:
                handler(message)

    @classmethod
    def save_event(cls, event: RawEvent, position: Optional[int] = None) -> Event:
        return cls.repository.save_event(event, position)

    @classmethod
    def save_command(cls, *args, **kwargs):
        raise NotImplementedError()
