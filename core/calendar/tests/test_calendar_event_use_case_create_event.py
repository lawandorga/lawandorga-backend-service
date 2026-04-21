from datetime import timedelta

import pytest
from django.utils import timezone

from core.calendar.models import CalendarEvent
from core.calendar.use_cases.event import create_event
from core.seedwork.domain_layer import DomainError
from core.tests import test_helpers


def test_create_event_minimal_inputs_persists_defaults(db):
    user_data = test_helpers.create_org_user(save=True)
    actor = user_data["org_user"]

    start = timezone.now()

    event = create_event(
        __actor=actor,
        title="Planning",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
    )

    assert event.pk is not None
    assert event.creator_id == actor.pk
    assert event.title == "Planning"
    assert event.event_type == CalendarEvent.EventType.MEETING
    assert event.start_time == start
    assert event.end_time is None
    assert event.description == ""
    assert event.location == ""
    assert event.recurrence_rule == ""
    assert event.recurrence_until is None


def test_create_event_with_optional_fields(db):
    user_data = test_helpers.create_org_user(save=True)
    actor = user_data["org_user"]

    start = timezone.now()
    end = start + timedelta(hours=2)
    until = (start + timedelta(days=10)).date()

    event = create_event(
        __actor=actor,
        title="Daily standup",
        event_type=CalendarEvent.EventType.APPOINTMENT,
        start_time=start,
        end_time=end,
        description="Talk about progress",
        location="Zoom",
        recurrence_rule="  FREQ=DAILY;INTERVAL=1  ",
        recurrence_until=until,
    )

    assert event.pk is not None
    assert event.end_time == end
    assert event.description == "Talk about progress"
    assert event.location == "Zoom"
    assert event.recurrence_rule == "FREQ=DAILY;INTERVAL=1"
    assert event.recurrence_until == until


def test_create_event_rejects_end_before_start(db):
    user_data = test_helpers.create_org_user(save=True)
    actor = user_data["org_user"]

    start = timezone.now()
    end = start - timedelta(minutes=5)

    with pytest.raises(DomainError):
        create_event(
            __actor=actor,
            title="Impossible",
            event_type=CalendarEvent.EventType.TASK,
            start_time=start,
            end_time=end,
        )
