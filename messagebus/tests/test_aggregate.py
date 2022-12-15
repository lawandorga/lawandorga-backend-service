from uuid import uuid4

from messagebus import DjangoAggregate, Event, MessageBus
from messagebus.impl.repository import Message


def test_django_aggregate_event_handling(db):
    metadata = {"total_miles": 0}

    class StubModel:
        def save(self, *args, **kwargs):
            # noop
            # django model would save
            pass

    class Car(DjangoAggregate, StubModel):
        def __init__(self):
            self.uuid = uuid4()

        def drive_to_location(self):
            self.add_event("DrivenToLocation", {"miles": 500}, metadata)

    def change_state(event: Event):
        event.metadata["total_miles"] += event.data["miles"]

    MessageBus.register_handler("DrivenToLocation", change_state)

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
