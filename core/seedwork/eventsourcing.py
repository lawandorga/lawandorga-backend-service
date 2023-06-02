from core.timeline.utils import camel_to_snake_case
from messagebus import Event


class EventSourced:
    def __init__(self, events: list[Event]) -> None:
        for event in events:
            self.mutate(event)
        self.new_events: list[Event] = []

    def mutate(self, event: Event):
        action = camel_to_snake_case(event.action)
        func = getattr(self, f"when_{action}")
        func(event)

    def apply(self, event: Event):
        self.new_events.append(event)
        self.mutate(event)
