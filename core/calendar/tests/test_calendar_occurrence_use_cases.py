from datetime import timedelta

import pytest
from django.utils import timezone

from core.calendar.models import (
    CalendarEvent,
    CalendarEventOccurrenceOverride,
    CalendarEventReminder,
    CalendarEventShare,
    RecurrenceRule,
)
from core.calendar.use_cases.occurrence import (
    cancel_event_occurrence,
    update_event_occurrence,
)
from core.calendar.use_cases.reminder import create_reminder
from core.seedwork.domain_layer import DomainError
from core.seedwork.use_case_layer.error import UseCaseError
from core.tests import test_helpers


def _now_without_microseconds():
    # dateutil expands recurrences with second precision
    return timezone.now().replace(microsecond=0)


def _create_weekly_event(actor, start=None):
    start = start or _now_without_microseconds() + timedelta(days=1)
    event = CalendarEvent.create(
        creator=actor,
        title="Standup",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=start + timedelta(hours=1),
        recurrence_rule=RecurrenceRule("FREQ=WEEKLY"),
    )
    event.save()
    return event


def _actor():
    return test_helpers.create_org_user(save=True)["org_user"]


def test_update_occurrence_creates_override(db):
    actor = _actor()
    event = _create_weekly_event(actor)
    slot = event.start_time + timedelta(days=7)
    moved_start = slot + timedelta(hours=2)

    override = update_event_occurrence(
        __actor=actor,
        event_uuid=event.uuid,
        original_start=slot,
        start_time=moved_start,
        title="Standup (moved)",
    )

    assert override.original_start == slot
    assert override.start_time == moved_start
    assert override.title == "Standup (moved)"
    assert override.end_time is None
    assert override.cancelled is False


def test_update_occurrence_twice_updates_same_override(db):
    actor = _actor()
    event = _create_weekly_event(actor)
    slot = event.start_time + timedelta(days=7)

    update_event_occurrence(
        __actor=actor, event_uuid=event.uuid, original_start=slot, title="First"
    )
    update_event_occurrence(
        __actor=actor, event_uuid=event.uuid, original_start=slot, location="Room 2"
    )

    overrides = CalendarEventOccurrenceOverride.objects.filter(event=event)
    assert overrides.count() == 1
    override = overrides.get()
    assert override.title == "First"
    assert override.location == "Room 2"


def test_update_occurrence_rejects_non_recurring_event(db):
    actor = _actor()
    start = timezone.now() + timedelta(days=1)
    event = CalendarEvent.create(
        creator=actor,
        title="One-off",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=start + timedelta(hours=1),
    )
    event.save()

    with pytest.raises(UseCaseError):
        update_event_occurrence(
            __actor=actor,
            event_uuid=event.uuid,
            original_start=start,
            title="Nope",
        )


def test_update_occurrence_rejects_non_slot(db):
    actor = _actor()
    event = _create_weekly_event(actor)
    not_a_slot = event.start_time + timedelta(days=3)

    with pytest.raises(UseCaseError):
        update_event_occurrence(
            __actor=actor,
            event_uuid=event.uuid,
            original_start=not_a_slot,
            title="Nope",
        )

    assert CalendarEventOccurrenceOverride.objects.count() == 0


def test_update_occurrence_rejects_users_without_edit_access(db):
    org = test_helpers.create_org("Shared Org", save=True)["org"]
    creator = test_helpers.create_org_user(
        email="creator@law-orga.de", org=org, save=True
    )["org_user"]
    viewer = test_helpers.create_org_user(
        email="viewer@law-orga.de", org=org, save=True
    )["org_user"]
    event = _create_weekly_event(creator)
    event.grant_access(
        by=creator,
        access_level=CalendarEventShare.AccessLevel.VIEW,
        shared_user=viewer,
    )
    slot = event.start_time + timedelta(days=7)

    with pytest.raises(DomainError):
        update_event_occurrence(
            __actor=viewer, event_uuid=event.uuid, original_start=slot, title="Nope"
        )


def test_update_occurrence_rejects_start_after_end(db):
    actor = _actor()
    event = _create_weekly_event(actor)
    slot = event.start_time + timedelta(days=7)

    with pytest.raises(DomainError):
        update_event_occurrence(
            __actor=actor,
            event_uuid=event.uuid,
            original_start=slot,
            start_time=slot + timedelta(hours=5),
            end_time=slot + timedelta(hours=1),
        )

    # A rejected edit must not leave an empty override behind.
    assert CalendarEventOccurrenceOverride.objects.count() == 0


def test_cancel_occurrence_sets_cancelled(db):
    actor = _actor()
    event = _create_weekly_event(actor)
    slot = event.start_time + timedelta(days=7)

    cancel_event_occurrence(__actor=actor, event_uuid=event.uuid, original_start=slot)

    override = CalendarEventOccurrenceOverride.objects.get(
        event=event, original_start=slot
    )
    assert override.cancelled is True


def test_cancel_occurrence_resyncs_reminders(db):
    actor = _actor()
    event = _create_weekly_event(actor)
    reminder = create_reminder(
        __actor=actor,
        event_uuid=event.uuid,
        minutes_before=60,
        method=CalendarEventReminder.Method.EMAIL,
    )
    assert reminder.original_start == event.start_time

    cancel_event_occurrence(
        __actor=actor, event_uuid=event.uuid, original_start=event.start_time
    )

    reminder.refresh_from_db()
    assert reminder.original_start == event.start_time + timedelta(weeks=1)
    assert reminder.remind_at == reminder.original_start - timedelta(minutes=60)


def test_moving_occurrence_resyncs_reminders(db):
    actor = _actor()
    event = _create_weekly_event(actor)
    reminder = create_reminder(
        __actor=actor,
        event_uuid=event.uuid,
        minutes_before=60,
        method=CalendarEventReminder.Method.EMAIL,
    )
    moved_start = event.start_time + timedelta(hours=3)

    update_event_occurrence(
        __actor=actor,
        event_uuid=event.uuid,
        original_start=event.start_time,
        start_time=moved_start,
    )

    reminder.refresh_from_db()
    assert reminder.original_start == event.start_time  # slot is unchanged
    assert reminder.remind_at == moved_start - timedelta(minutes=60)


def test_cancel_after_update_keeps_override_fields(db):
    actor = _actor()
    event = _create_weekly_event(actor)
    slot = event.start_time + timedelta(days=7)

    update_event_occurrence(
        __actor=actor, event_uuid=event.uuid, original_start=slot, title="Moved"
    )
    cancel_event_occurrence(__actor=actor, event_uuid=event.uuid, original_start=slot)

    override = CalendarEventOccurrenceOverride.objects.get(
        event=event, original_start=slot
    )
    assert override.cancelled is True
    assert override.title == "Moved"
    assert CalendarEventOccurrenceOverride.objects.count() == 1
