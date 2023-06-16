from logging import getLogger
from typing import Callable, Optional, Type, TypeVar

from messagebus.domain.event import Event
from messagebus.domain.message import Message

logger = getLogger("messagebus")


E = TypeVar("E", bound=Event)


class MessageBus:
    """
    The MessageBus is the central point of the messagebus package.
    It is responsible for registering handlers and dispatching events to them.
    """

    handlers: dict[Type[Event], set[Callable]] = {}
    event_models: Optional[dict[str, Type[Event]]] = None

    @classmethod
    def _run_nesting_check(cls, event_class: Type[Event]) -> None:
        if event_class.__qualname__.count(".") != 1:
            raise ValueError(
                f"Event '{event_class.__name__}' is not nested correctly inside a "
                "class. The qualname is '{event_class.__qualname__}' but should "
                "contain exactly one dot."
            )

    @classmethod
    def _run_duplicate_check(cls, event_class: Type[Event]) -> None:
        cls_names = [cls._get_name() for cls in Event.__subclasses__()]
        if cls_names.count(event_class._get_name()) > 1:
            raise ValueError(
                f"Event '{event_class._get_name()}' is defined more than once."
            )

    @classmethod
    def run_checks(cls):
        for event_type in Event.__subclasses__():
            cls._run_nesting_check(event_type)
            cls._run_duplicate_check(event_type)

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
    def reset(cls) -> None:
        cls.handlers = {}
        cls.event_models = None

    @classmethod
    def register_handler(cls, event_class: Type[Event], handler: Callable):
        if not issubclass(event_class, Event):
            raise TypeError(
                f"The event class is of type '{event_class}' but should "
                f"be a subclass of '{Event}' does not fit."
            )

        if event_class not in cls.handlers:
            cls.handlers[event_class] = set()

        cls.handlers[event_class].add(handler)

        logger.info(
            f"Handler {handler.__name__} registered for action '{event_class}'."
        )

    @classmethod
    def load(cls) -> None:
        if cls.event_models is not None:
            return

        cls.event_models = {}

        for sc in Event.__subclasses__():
            cls._run_nesting_check(sc)
            cls._run_duplicate_check(sc)

            if sc._get_name() in cls.event_models:
                raise ValueError(f"Event '{sc._get_name()}' is defined more than once.")
            cls.event_models[sc._get_name()] = sc
            logger.info(f"Event {sc._get_name()} loaded.")

    @classmethod
    def get_event_model(cls, name: str) -> Type[Event]:
        if cls.event_models is None:
            cls.load()

        assert cls.event_models is not None

        try:
            model = cls.event_models[name]
        except KeyError:
            cls.event_models = None
            cls.load()
            assert cls.event_models is not None
            model = cls.event_models[name]

        return model

    @classmethod
    def handle(cls, message: Event):
        message_type = type(message)
        if message_type in cls.handlers:
            for handler in cls.handlers[message_type]:
                handler(message)

    @classmethod
    def get_event_from_message(cls, aggregate_name: str, message: Message) -> Event:
        name = f"{aggregate_name}.{message.action}"
        event_model = cls.get_event_model(name)

        event = event_model(
            **message.data,
            metadata=message.metadata,
        )

        return event
