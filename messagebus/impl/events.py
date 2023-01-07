from typing import Optional, Type

from messagebus import MessageBus, RawEvent
from messagebus.domain.data import EventData, JsonDict
from messagebus.impl.object import Object
from messagebus.impl.factory import create_event_from_aggregate


class Events:
    def __init__(self, obj: Object, events: list[Type[EventData]]):
        for event in events:
            MessageBus.register_event_model(event)
        self.__object = obj
        self.__events: list[RawEvent] = []

    @property
    def events(self):
        return self.__events

    def add(self, data: EventData, metadata: Optional[JsonDict] = None):
        event = create_event_from_aggregate(self.__object, data, metadata)
        self.__events.append(event)

    def reset(self):
        self.__events = []
