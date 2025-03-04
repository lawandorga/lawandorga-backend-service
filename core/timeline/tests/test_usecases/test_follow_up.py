from django.utils import timezone

from core.seedwork import test_helpers
from core.timeline.models.follow_up import TimelineFollowUp
from core.timeline.tests import helpers
from core.timeline.usecases.follow_up import (
    create_follow_up,
    delete_follow_up,
    set_follow_up_as_done,
    update_follow_up,
)


def test_follow_up_creation(db):
    user = test_helpers.create_org_user()["org_user"]
    folder = test_helpers.create_folder(user=user)["folder"]
    follow_up = create_follow_up(
        user,
        title="Title",
        text="test",
        time=timezone.now(),
        folder_uuid=folder.uuid,
    )
    assert follow_up.text == "test"
    assert TimelineFollowUp.objects.count() == 1


def test_update_follow_up(db):
    user = test_helpers.create_org_user(save=True)["org_user"]
    follow_up = helpers.create_follow_up(user=user)
    follow_up = update_follow_up(
        __actor=user,
        uuid=follow_up.uuid,
        title="New Title",
        text=None,
        time=None,
        is_done=None,
    )
    assert follow_up.title == "New Title"


def test_delete_follow_up(db):
    user = test_helpers.create_org_user(save=True)["org_user"]
    follow_up = helpers.create_follow_up(user=user)
    delete_follow_up(
        __actor=user,
        uuid=follow_up.uuid,
    )
    assert TimelineFollowUp.objects.count() == 0


def test_follow_up_done(db):
    user = test_helpers.create_org_user(save=True)["org_user"]
    follow_up = helpers.create_follow_up(user=user)
    set_follow_up_as_done(
        __actor=user,
        uuid=follow_up.uuid,
    )
    assert TimelineFollowUp.objects.filter(is_done=True).count() == 1
