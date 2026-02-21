from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import Client
from django.utils.module_loading import import_string

from core.seedwork.use_case_layer import use_case
from core.usecases import USECASES
from messagebus.domain.collector import EventCollector
from messagebus.domain.event import Event


class Car:
    class Driven(Event):
        miles: int


EVENTS: list[Event] = []
CALLED = False


def handle_events(collector: EventCollector):
    global CALLED
    CALLED = True
    while event := collector.pop():
        for e in EVENTS:
            if e.uuid == event.uuid and getattr(e, "miles", 0) >= getattr(
                event, "miles", 0
            ):
                raise Exception("Event already handled")
        EVENTS.append(event)


@use_case
def example(__actor: AnonymousUser, a: int, collector: EventCollector):
    uuid = uuid4()
    collector.collect(Car.Driven(miles=1, uuid=uuid))
    collector.collect(Car.Driven(miles=2, uuid=uuid))
    collector.collect(Car.Driven(miles=3, uuid=uuid))
    collector.collect(Car.Driven(miles=4, uuid=uuid))
    collector.collect(Car.Driven(miles=5, uuid=uuid))
    collector.collect(Car.Driven(miles=6, uuid=uuid))


def test_event_are_being_handled_in_order(db):
    callbacks: list = import_string(settings.USECASE_CALLBACKS)  # type: ignore
    callbacks.clear()
    callbacks.append(handle_events)

    USECASES["test"] = example
    client = Client()

    def post_command(action: str):
        return client.post(
            "/api/command/",
            data={"action": action, "a": 1},
        )

    def run_requests_in_parallel():
        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(post_command, "test")
            future2 = executor.submit(post_command, "test")
            resp1 = future1.result()
            resp2 = future2.result()
            assert resp1.status_code == 200
            assert resp2.status_code == 200

    run_requests_in_parallel()

    global CALLED
    assert CALLED
