from uuid import uuid4

from core.seedwork import test_helpers
from core.timeline.domain import TimelineEvent
from core.timeline.use_cases import create_timeline_event


def test_create_raw():
    user = test_helpers.create_raw_org_user()
    folder = test_helpers.create_raw_folder(user)
    event = TimelineEvent.create(
        text="test", folder=folder, org_pk=user.org_id, by=user.uuid
    )
    assert event.text == "test"


def test_create_usecase(db):
    user = test_helpers.create_rlc_user()["rlc_user"]
    folder = test_helpers.create_folder(user=user)["folder"]
    event = create_timeline_event(user, "test", folder.uuid)
    assert event.text == "test"


def test_different_uuids():
    user = test_helpers.create_raw_org_user()
    folder = test_helpers.create_raw_folder(user)
    event1 = TimelineEvent.create(
        text="test", folder=folder, org_pk=user.org_id, by=user.uuid
    )
    event2 = TimelineEvent.create(
        text="test", folder=folder, org_pk=user.org_id, by=user.uuid
    )
    assert event1.uuid != event2.uuid


def test_created_events_uuid_different():
    e1 = TimelineEvent.Created(text="test", by=uuid4(), folder_uuid=uuid4(), org_pk=1)
    e2 = TimelineEvent.Created(text="test", by=uuid4(), folder_uuid=uuid4(), org_pk=1)
    assert e1.uuid != e2.uuid
