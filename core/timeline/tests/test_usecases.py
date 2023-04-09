import pytest
from django.conf import settings

from core.seedwork import test_helpers
from core.timeline.domain import TimelineEvent
from core.timeline.repository import (
    DjangoTimelineEventRepository,
    InMemoryTimelineEventRepository,
    TimelineEventRepository,
)


@pytest.fixture
def in_memory():
    default = settings.REPOSITORY_TIMELINE_EVENT
    settings.REPOSITORY_TIMELINE_EVENT = (
        "core.timeline.repository.InMemoryTimelineEventRepository"
    )
    yield
    settings.REPOSITORY_TIMELINE_EVENT = default


def test_in_memory_repository(in_memory):
    r = TimelineEventRepository(None)
    assert isinstance(r, InMemoryTimelineEventRepository)


def test_settings_repository():
    r = TimelineEventRepository(None)
    assert isinstance(r, DjangoTimelineEventRepository)
    settings.REPOSITORY_TIMELINE_EVENT = (
        "core.timeline.repository.InMemoryTimelineEventRepository"
    )
    r = TimelineEventRepository(None)
    print(r)
    assert isinstance(r, InMemoryTimelineEventRepository)


def test_create():
    user = test_helpers.create_raw_org_user()
    folder = test_helpers.create_raw_folder(user)
    event = TimelineEvent.create(text="test", folder=folder, org_pk=user.org_id)
    assert event.text == "test"


def test_repository(in_memory):
    user = test_helpers.create_raw_org_user()
    folder = test_helpers.create_raw_folder(user)
    event1 = TimelineEvent.create(text="test", folder=folder, org_pk=user.org_id)
    r = TimelineEventRepository(None)
    r.save(event1, by=user)
    event2 = r.load(event1.uuid, user, folder)
    assert event2.text == "test"
