from core.seedwork import test_helpers
from core.timeline.domain import TimelineEvent
from core.timeline.repository import (
    EventStoreTimelineEventRepository,
    TimelineEventRepository,
)
from messagebus.impl.store import InMemoryEventStore


def test_repository():
    r = TimelineEventRepository(InMemoryEventStore())
    assert isinstance(r, EventStoreTimelineEventRepository)


def test_create_raw():
    user = test_helpers.create_raw_org_user()
    folder = test_helpers.create_raw_folder(user)
    event = TimelineEvent.create(text="test", folder=folder, org_pk=user.org_id)
    assert event.text == "test"


def test_create_in_memory():
    user = test_helpers.create_raw_org_user()
    folder = test_helpers.create_raw_folder(user)
    event1 = TimelineEvent.create(text="test", folder=folder, org_pk=user.org_id)
    r = EventStoreTimelineEventRepository(InMemoryEventStore())
    r.save(event1, by=user)
    event2 = r.load(event1.uuid, user, folder)
    assert event2.text == "test"
