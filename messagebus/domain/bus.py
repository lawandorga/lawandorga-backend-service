from logging import getLogger
from typing import Callable, Optional, Type, TypeVar

from messagebus.domain.event import Event

logger = getLogger("messagebus")


E = TypeVar("E", bound=Event)


Handlers = dict[Type[E], list[Callable[[E], None]]]


class MessageBus:
    """
    The MessageBus is the central point of the messagebus package.
    It is responsible for registering handlers and dispatching events to them.
    """

    handlers: dict[Type[Event], set[Callable]] = {}
    event_models: Optional[dict[str, Type[Event]]] = None

    def _run_nesting_check(self, event_class: Type[Event]) -> None:
        if event_class.__qualname__.count(".") != 1:
            raise ValueError(
                f"Event '{event_class.__name__}' is not nested correctly inside a "
                "class. The qualname is '{event_class.__qualname__}' but should "
                "contain exactly one dot."
            )

    def _run_duplicate_check(self, event_class: Type[Event]) -> None:
        cls_names = [cls._get_name() for cls in Event.__subclasses__()]
        if cls_names.count(event_class._get_name()) > 1:
            raise ValueError(
                f"Event '{event_class._get_name()}' is defined more than once."
            )

    def run_checks(self):
        for event_type in Event.__subclasses__():
            self._run_nesting_check(event_type)
            self._run_duplicate_check(event_type)

    def register_handler(self, event_class: Type[Event], handler: Callable):
        if not issubclass(event_class, Event):
            raise TypeError(
                f"The event class is of type '{event_class}' but should "
                f"be a subclass of '{Event}' does not fit."
            )

        if event_class not in self.handlers:
            self.handlers[event_class] = set()

        self.handlers[event_class].add(handler)

        logger.info(
            f"Handler {handler.__name__} registered for action '{event_class}'."
        )

    def handle(self, message: Event):
        message_type = type(message)
        if message_type in self.handlers:
            for handler in self.handlers[message_type]:
                handler(message)
