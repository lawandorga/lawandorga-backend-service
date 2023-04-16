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
        DomainMessage(action="action1", data={"this": "that"}),
        DomainMessage(action="action2", data={"this": "that"}),
    ]
    r.append("test", events)
    events = r.load("test")
    assert (
        len(events) == 2
        and events[0].metadata["position"] == 1
        and events[1].metadata["position"] == 2
    )


def test_singleton_pattern():
    r1 = InMemoryEventStore()
    r2 = InMemoryEventStore()
    assert r1 is r2


def test_django_event_store_position(db):
    r = DjangoEventStore()
    events = [
        DomainMessage(action="action1", data={"this": "that"}),
        DomainMessage(action="action2", data={"this": "that"}),
    ]
    r.append("teststream12", events)
    events = r.load("teststream12")
    assert (
        len(events) == 2
        and events[0].metadata["position"] == 1
        and events[1].metadata["position"] == 2
    )


def test_empty_array(db):
    r1 = DjangoEventStore()
    assert isinstance(r1, DjangoEventStore)
    r1.append("none", [])
    r2 = InMemoryEventStore()
    assert isinstance(r2, InMemoryEventStore)
    r2.append("none", [])


def test_metadata_is_saved():
    r = InMemoryEventStore()
    events = [
        DomainMessage(action="action1", data={"this": "that"}, metadata={"foo": "bar"}),
    ]
    r.append("testMeta1", events)
    events = r.load("testMeta1")
    assert len(events) == 1 and events[0].metadata["foo"] == "bar"


def test_metadata_is_saved_django(db):
    r = DjangoEventStore()
    events = [
        DomainMessage(action="action1", data={"this": "that"}, metadata={"foo": "bar"}),
    ]
    r.append("testmeta2", events)
    events = r.load("testmeta2")
    assert len(events) == 1 and events[0].metadata["foo"] == "bar"


def test_metadata_contains_time_position_and_stream_name(db):
    i = 4
    for r in [InMemoryEventStore(), DjangoEventStore()]:
        events = [
            DomainMessage(action="action1", data={"this": "that"}),
        ]
        r.append(f"testmeta{i}", events)
        events = r.load(f"testmeta{i}")
        assert (
            len(events) == 1
            and events[0].metadata["position"] == 1
            and events[0].metadata["stream_name"] == f"testmeta{i}"
            and events[0].metadata["time"] is not None
        )
        i += 1


def test_like_query(db):
    r = DjangoEventStore()
    events = [
        DomainMessage(action="action1", data={"this": "that"}),
    ]
    r.append("testlike1", events)
    events = r.load("testli", exact=False)
    assert len(events) == 1


def test_like_query_memory(db):
    r = DjangoEventStore()
    events = [
        DomainMessage(action="action1", data={"this": "that"}),
    ]
    r.append("testab1", events)
    events = r.load("testab", exact=False)
    assert len(events) == 1
