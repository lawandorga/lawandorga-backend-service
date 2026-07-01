from datetime import timedelta

from django.utils import timezone

from core.calendar.models import CalendarEvent
from core.calendar.use_cases.event import create_event, update_event
from core.tests import test_helpers


def test_update_event_keeps_end_time_when_set_to_none(db):
    user_data = test_helpers.create_org_user(save=True)
    actor = user_data["org_user"]
    start = timezone.now()

    event = create_event(
        __actor=actor,
        title="Sync",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=start + timedelta(hours=1),
    )

    original_end_time = event.end_time

    update_event(__actor=actor, event_uuid=event.uuid, end_time=None)

    event.refresh_from_db()
    assert event.end_time == original_end_time


def test_update_event_can_clear_the_recurrence_until(db):
    user_data = test_helpers.create_org_user(save=True)
    actor = user_data["org_user"]
    start = timezone.now()

    event = create_event(
        __actor=actor,
        title="Standup",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=start + timedelta(hours=1),
        recurrence_rule="FREQ=DAILY",
        recurrence_until=(start + timedelta(days=7)).date(),
    )

    update_event(
        __actor=actor,
        event_uuid=event.uuid,
        recurrence_rule="",
        recurrence_until=None,
    )

    event.refresh_from_db()
    assert event.recurrence_until is None
