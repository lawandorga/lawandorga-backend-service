from logging import getLogger
from typing import Callable, Optional, Type, TypeVar

from messagebus.domain.event import Event
from messagebus.domain.repository import MessageBusRepository

logger = getLogger("messagebus")


E = TypeVar("E", bound=Event)


class MessageBus:
    handlers: dict[Type[Event], set[Callable]] = {}
    repository: Type[MessageBusRepository]
    event_models: dict[str, Type[Event]] = {}

    @classmethod
    def run_checks(cls):
        for cls in Event.__subclasses__():
            if cls.__qualname__.count(".") != 1:
                raise ValueError(
                    f"Event '{cls.__name__}' is not nested correctly inside a class. The qualname is '{cls.__qualname__}' but should contain exactly one dot."
                )

            cls_names = [cls.__qualname__ for cls in Event.__subclasses__()]
            if cls_names.count(cls.__qualname__) > 1:
                raise ValueError(
                    f"Event '{cls.__qualname__}' is defined more than once."
                )

    @classmethod
    def handler(
        cls, on: Type[E] | list[Type[E]]
    ) -> Callable[[Callable[[E], None]], Callable[[E], None]]:
        def wrapper(handler: Callable[[E], None]) -> Callable[[E], None]:
            when = on if isinstance(on, list) else [on]

            for event_class in when:
                cls.register_handler(event_class, handler)

            return handler

        return wrapper

    @classmethod
    def set_repository(cls, repository: Type[MessageBusRepository]):
        cls.repository = repository

    @classmethod
    def register_handler(cls, event_class: Type[Event], handler: Callable):
        if not issubclass(event_class, Event):
            raise TypeError(
                f"The event class is of type '{event_class}' but should be a subclass of '{Event}' does not fit."
            )

        if event_class not in cls.handlers:
            cls.handlers[event_class] = set()

        cls.handlers[event_class].add(handler)

        logger.info(
            f"Handler {handler.__name__} registered for action '{event_class}'."
        )

    @classmethod
    def get_event_model(cls, name: str) -> Type[Event]:
        for sc in Event.__subclasses__():
            cls.event_models = {sc._get_name(): sc}
        # raise Exception(cls.event_models)
        return cls.event_models[sc._get_name()]

    @classmethod
    def handle(cls, message: Event):
        message_type = type(message)
        if message_type in cls.handlers:
            for handler in cls.handlers[message_type]:
                handler(message)

    @classmethod
    def save_event(cls, event: Event, position: Optional[int] = None) -> Event:
        return cls.repository.save_event(event, position)

    @classmethod
    def save_command(cls, *args, **kwargs):
        raise NotImplementedError()
