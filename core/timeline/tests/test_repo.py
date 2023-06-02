from django.utils import timezone

from core.seedwork import test_helpers
from core.timeline.domain import TimelineEvent
from core.timeline.repository import (
    EventStoreTimelineEventRepository,
    TimelineEventRepository,
)
from messagebus.impl.store import InMemoryEventStore
from messagebus.impl.store.django import DjangoEventStore


def test_repository_type():
    r = TimelineEventRepository(InMemoryEventStore())
    assert isinstance(r, EventStoreTimelineEventRepository)


def test_create_in_memory():
    user = test_helpers.create_raw_org_user()
    folder = test_helpers.create_raw_folder(user)
    event1 = TimelineEvent.create(
        text="test",
        title="Title",
        folder=folder,
        org_pk=user.org_id,
        by=user.uuid,
        time=timezone.now(),
    )
    r = EventStoreTimelineEventRepository(InMemoryEventStore())
    r.save(event1, by=user)
    event2 = r.load(event1.uuid, user, folder)
    assert event2.text == "test"


def test_create_in_db(db):
    user = test_helpers.create_raw_org_user()
    folder = test_helpers.create_raw_folder(user)
    event1 = TimelineEvent.create(
        text="test",
        title="Title",
        folder=folder,
        org_pk=user.org_id,
        by=user.uuid,
        time=timezone.now(),
    )
    r = EventStoreTimelineEventRepository(DjangoEventStore())
    r.save(event1, by=user)
    event2 = r.load(event1.uuid, user, folder)
    assert event2.text == "test"


def test_list_in_memory():
    user = test_helpers.create_raw_org_user()
    folder = test_helpers.create_raw_folder(user)
    event1 = TimelineEvent.create(
        text="test",
        folder=folder,
        title="Title",
        org_pk=user.org_id,
        by=user.uuid,
        time=timezone.now(),
    )
    event2 = TimelineEvent.create(
        text="test2",
        title="Title",
        folder=folder,
        org_pk=user.org_id,
        by=user.uuid,
        time=timezone.now(),
    )
    assert event1.uuid != event2.uuid
    r = EventStoreTimelineEventRepository(InMemoryEventStore())
    r.save(event1, by=user)
    r.save(event2, by=user)
    events = r.list(folder, user)
    assert len(events) == 2
    assert events[0].text == "test" and events[1].text == "test2"
