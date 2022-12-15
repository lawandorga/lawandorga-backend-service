from typing import Any, Optional

from django.db import transaction

from messagebus.domain.bus import MessageBus
from messagebus.domain.event import Event, JsonDict
from messagebus.impl.factory import create_event_from_aggregate


class DjangoAggregate:
    uuid: Any  # Any because of django's models.UUIDField
    events: list[Event]

    def save(self, *args, **kwargs):
        events = []

        if not hasattr(self, "events"):
            self.events = []

        with transaction.atomic():
            super().save(*args, **kwargs)
            for event in self.events:
                event = MessageBus.save_event(event)
                events.append(event)

        # reset the events so that a second save does not trigger them again
        self.events = []

        # let the messagebus handle the events
        for event in events:
            MessageBus.handle(event)

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
