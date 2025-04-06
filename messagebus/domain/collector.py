from messagebus.domain.event import Event


class EventCollector:
    events: list[Event]

    def __init__(self):
        self.events = []

    def collect(self, event: Event):
        self.events.append(event)

    def pop(self):
        return self.events.pop(0) if self.events else None

    def clear_events(self):
        self.events.clear()
