from typing import Any, Callable, Optional

from django.db import transaction

from messagebus.domain.bus import MessageBus
from messagebus.domain.event import Event, JsonDict
from messagebus.impl.factory import create_event_from_aggregate


class DjangoAggregate:
    uuid: Any  # Any because of django's models.UUIDField
    events: list[Event]

    def __save_or_delete(self, func: Callable, *args, **kwargs):
        events = []

        if not hasattr(self, "events"):
            self.events = []

        with transaction.atomic():
            func(*args, **kwargs)
            for event in self.events:
                event = MessageBus.save_event(event)
                events.append(event)

        # reset the events so that a second save does not trigger them again
        self.events = []

        # let the messagebus handle the events
        for event in events:
            MessageBus.handle(event)

    def save(self, *args, **kwargs):
        self.__save_or_delete(super().save)

    def delete(self, *args, **kwargs):
        self.__save_or_delete(super().delete)

    def add_event(
        self,
        name: str,
        data: Optional[JsonDict] = None,
        metadata: Optional[JsonDict] = None,
    ):
        if not hasattr(self, "events"):
            self.events = []

        # create the event
        event = create_event_from_aggregate(self, name, data, metadata)
        self.events.append(event)
