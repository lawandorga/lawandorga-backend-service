from uuid import uuid4

from core.seedwork.aggregate import Aggregate
from core.seedwork.events_addon import EventsAddon
from messagebus import Event, EventData, MessageBus
from messagebus.impl.repository import Message


class StubModel:
    def save(self, raise_exception=False):
        if raise_exception:
            raise ValueError("It was supposed to happen.")

    def delete(self):
        pass


class Driven(EventData):
    miles: int


class Car(Aggregate, StubModel):
    addons = {"events": EventsAddon}
    events: EventsAddon

    def __init__(self):
        super().__init__()
        self.uuid = uuid4()

    def drive(self, miles=100):
        self.events.add(Driven(miles=miles))


def test_events_are_handled_and_saved(db):
    miles = 0

    @MessageBus.handler(on=Driven)
    def calculate_miles(event: Event[Driven]):
        nonlocal miles
        miles += event.data.miles

    car = Car()
    car.drive(500)
    car.save()

    assert miles == 500 and Message.objects.count() == 1


def test_events_are_saved_atomic(db):
    miles = 0

    @MessageBus.handler(on=Driven)
    def calculate_miles(event: Event[Driven]):
        nonlocal miles
        miles += event.data.miles

    car = Car()
    car.drive(500)
    try:
        car.save(raise_exception=True)
    except ValueError:
        pass

    assert miles == 0 and Message.objects.count() == 0


def test_events_are_handled_non_atomic(db):
    @MessageBus.handler(on=Driven)
    def calculate_miles(_: Event[Driven]):
        raise ValueError("It is supposed to happen.")

    car = Car()
    car.drive(500)
    try:
        car.save()
    except ValueError:
        pass

    assert Message.objects.count() == 1
