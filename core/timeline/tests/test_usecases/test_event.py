from django.utils import timezone

from core.tests import test_helpers
from core.timeline.models.event import TimelineEvent
from core.timeline.tests import helpers
from core.timeline.use_cases.event import create_event, delete_event, update_event


def test_event_creation(db):
    user = test_helpers.create_org_user()["org_user"]
    folder = test_helpers.create_folder(user=user)["folder"]
    event = create_event(
        user,
        title="Title",
        text="test",
        time=timezone.now(),
        folder_uuid=folder.uuid,
    )
    assert event.text == "test"
    assert TimelineEvent.objects.count() == 1


def test_update_event(db):
    user = test_helpers.create_org_user(save=True)["org_user"]
    event = helpers.create_event(user=user)
    event = update_event(
        __actor=user,
        uuid=event.uuid,
        title="New Title",
        text=None,
        time=None,
    )
    assert event.title == "New Title"


def test_delete_event(db):
    user = test_helpers.create_org_user(save=True)["org_user"]
    event = helpers.create_event(user=user)
    delete_event(
        __actor=user,
        uuid=event.uuid,
    )
    assert TimelineEvent.objects.count() == 0
