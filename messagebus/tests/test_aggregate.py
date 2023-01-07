from uuid import UUID, uuid4

from messagebus import Event, MessageBus
from messagebus.domain.data import EventData
from messagebus.impl.factory import create_event_from_aggregate
from messagebus.impl.repository import Message


@MessageBus.event
class DrivenToLocation(EventData):
    miles: int


class StubModel:
    uuid: UUID

    def __init__(self):
        self.events = []

    def save(self, *args, **kwargs):
        events = []

        for raw_event in self.events:
            event = MessageBus.save_event(raw_event)
            events.append(event)

        # reset the events so that a second save does not trigger them again
        self.events = []

        # let the messagebus handle the events
        for event in events:
            MessageBus.handle(event)

    def add_event(self, data: EventData, metadata: dict):
        event = create_event_from_aggregate(self, data, metadata)
        self.events.append(event)


def test_django_aggregate_event_handling(db):
    metadata = {"total_miles": 0}

    class Car(StubModel):
        def __init__(self):
            super().__init__()
            self.uuid = uuid4()

        def drive_to_location(self):
            self.add_event(DrivenToLocation(miles=500), metadata)

    def change_state(event: Event):
        event.metadata["total_miles"] += event.data.miles

    MessageBus.register_handler(DrivenToLocation, change_state)

    car = Car()
    car.drive_to_location()
    car.save()

    assert 1 == Message.objects.filter(action="DrivenToLocation").count()
    assert metadata["total_miles"] == 500

    # assert only saving the model calls the event handlers
    car.drive_to_location()
    assert metadata["total_miles"] == 500

    car.save()
    assert metadata["total_miles"] == 1000
