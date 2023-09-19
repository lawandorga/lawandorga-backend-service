from django.test import Client
from django.utils import timezone

from core.seedwork import test_helpers
from core.timeline.models.follow_up import TimelineFollowUp


def test_follow_up_creation_on_api(db):
    user = test_helpers.create_rlc_user()
    rlc_user = user["rlc_user"]
    folder = test_helpers.create_folder(user=rlc_user)["folder"]
    client = Client()
    client.login(**user)
    response = client.post(
        "/api/command/",
        data={
            "action": "create_follow_up",
            "title": "Title",
            "text": "test",
            "time": timezone.now(),
            "folder_uuid": folder.uuid,
        },
        content_type="application/json",
    )
    assert response.status_code == 200
    assert TimelineFollowUp.objects.count() == 1
