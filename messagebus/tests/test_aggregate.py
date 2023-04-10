from uuid import UUID, uuid4

from messagebus import Event, MessageBus
from messagebus.domain.store import EventStore
from messagebus.impl.message import Message


class StubModel:
    uuid: UUID

    def __init__(self):
        self.events = []

    def save(self, *args, **kwargs):
        events = []

        for raw_event in self.events:
            stream_name = f"{self.__class__.__name__}-{self.uuid}"
            EventStore().append(stream_name, [raw_event])
            events.append(raw_event)

        # reset the events so that a second save does not trigger them again
        self.events = []

        # let the messagebus handle the events
        for event in events:
            MessageBus.handle(event)

    def add_event(self, event: Event, metadata: dict):
        event.set_aggregate_uuid(self.uuid)
        self.events.append(event)


class Car(StubModel):
    class DrivenToLocation(Event):
        miles: int

    def __init__(self):
        super().__init__()
        self.uuid = uuid4()

    def drive_to_location(self):
        self.add_event(Car.DrivenToLocation(miles=500), metadata={})


def test_django_aggregate_event_handling(db):
    metadata = {"total_miles": 0}

    def change_state(event: Car.DrivenToLocation):
        metadata["total_miles"] += event.miles

    MessageBus.register_handler(Car.DrivenToLocation, change_state)

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
