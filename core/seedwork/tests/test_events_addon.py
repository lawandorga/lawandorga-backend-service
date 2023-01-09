from contextlib import ContextDecorator
from uuid import uuid4

import pytest

from core.seedwork.aggregate import Aggregate
from core.seedwork.events_addon import EventsAddon
from messagebus import Event, EventData, MessageBus
from messagebus.impl.repository import (
    DjangoMessageBusRepository,
    InMemoryMessageBusRepository,
)


@pytest.fixture
def inmemory():
    MessageBus.set_repository(InMemoryMessageBusRepository)
    InMemoryMessageBusRepository.messages = []
    MessageBus.handlers = {}
    yield
    MessageBus.set_repository(DjangoMessageBusRepository)


class Atomic(ContextDecorator):
    inside = ""

    def __init__(self):
        self.__class__.inside = ""

    def __enter__(self):
        self.__class__.inside = "Y"

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__class__.inside = "N"


class StubModel:
    def save(self, raise_exception=False):
        assert Atomic.inside == "Y"
        if raise_exception:
            raise ValueError("It was supposed to happen.")

    def delete(self):
        pass


class Driven(EventData):
    miles: int


class Car(Aggregate, StubModel):
    addons = {"events": EventsAddon}
    events: EventsAddon

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uuid = uuid4()

    def drive(self, miles=100):
        self.events.add(Driven(miles=miles))


def test_events_are_handled_and_saved(inmemory):
    miles = 0

    @MessageBus.handler(on=Driven)
    def calculate_miles(event: Event[Driven]):
        assert Atomic.inside == "N"
        nonlocal miles
        miles += event.data.miles

    car = Car(atomic_context=Atomic)
    car.drive(500)
    car.save()

    assert miles == 500 and len(InMemoryMessageBusRepository.messages) == 1


def test_events_are_saved_atomic(inmemory):
    @MessageBus.handler(on=Driven)
    def calculate_miles(_: Event[Driven]):
        assert False

    car = Car(atomic_context=Atomic)
    car.drive(200)
    try:
        car.save(raise_exception=True)
    except ValueError:
        pass

    assert len(InMemoryMessageBusRepository.messages) == 0


def test_events_are_handled_non_atomic(inmemory):
    @MessageBus.handler(on=Driven)
    def calculate_miles(_: Event[Driven]):
        assert Atomic.inside == "N"
        raise ValueError("It is supposed to happen.")

    car = Car(atomic_context=Atomic)
    car.drive(500)
    try:
        car.save()
    except ValueError:
        pass

    assert len(InMemoryMessageBusRepository.messages) == 1
