from core.seedwork import test_helpers
from core.timeline.use_cases import create_timeline_event


def test_create():
    user = test_helpers.create_raw_org_user()
    event = create_timeline_event(user, text="test")
    assert event.text == "test"
