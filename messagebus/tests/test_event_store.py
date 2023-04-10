from django.conf import settings

from messagebus.domain.message import DomainMessage
from messagebus.domain.store import EventStore
from messagebus.impl.store import DjangoEventStore, InMemoryEventStore


def test_settings_repository():
    r = EventStore()
    assert isinstance(r, DjangoEventStore)
    settings.MESSAGEBUS_EVENT_STORE = "messagebus.impl.store.InMemoryEventStore"
    r = EventStore()
    assert isinstance(r, InMemoryEventStore)


def test_in_memory_event_store_position():
    r = InMemoryEventStore()
    events = [
        DomainMessage(stream_name="test", action="action1", data={"this": "that"}),
        DomainMessage(stream_name="test", action="action2", data={"this": "that"}),
    ]
    r.append(events)
    events = r.load("test")
    assert len(events) == 2 and events[0].position == 1 and events[1].position == 2


def test_django_event_store_position(db):
    r = DjangoEventStore()
    events = [
        DomainMessage(stream_name="test", action="action1", data={"this": "that"}),
        DomainMessage(stream_name="test", action="action2", data={"this": "that"}),
    ]
    r.append(events)
    events = r.load("test")
    assert len(events) == 2 and events[0].position == 1 and events[1].position == 2
