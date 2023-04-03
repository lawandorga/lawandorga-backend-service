from uuid import uuid4, UUID
from messagebus import Event
from messagebus.domain.data import EventData


class EventSourced:
    def __init__(self, events: list[Event]) -> None:
        for event in events:
            self.mutate(event)
        self.new_events = []

    def mutate(self, event: Event):
        func = getattr(self, f"when_{event.action}")
        func(**event.data)

    def generate_event(self, event: EventData) -> Event:
        pass

    def apply(self, event: EventData):
        self.new_events.append(event)
        self.mutate(event)


class Created(EventData):
    text: str
    uuid: UUID = uuid4()


class TimelineEvent(EventSourced):
    def __init__(self, events: list[Event] = []):
        super().__init__(events)
    
    def create(self, text: str):
        self.apply(Created(text=text))

    def when_created(self, text: str):
        self.text = text

    def when_information_updated(self, text=None):
        if text is not None:
            self.text = text

    def when_deleted(self):
        pass
