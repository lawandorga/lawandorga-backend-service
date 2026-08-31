from datetime import timedelta

import pytest
from django.utils import timezone

from core.calendar.models import (
    CalendarEvent,
    CalendarEventReminder,
    CalendarEventShare,
)
from core.calendar.use_cases.event import create_event, update_event
from core.calendar.use_cases.reminder import (
    create_reminder,
    delete_reminder,
    update_reminder,
)
from core.seedwork.domain_layer import DomainError
from core.seedwork.use_case_layer.error import UseCaseError
from core.tests import test_helpers


def _now_without_microseconds():
    # dateutil expands recurrences with second precision
    return timezone.now().replace(microsecond=0)


def _create_event(actor, start=None):
    start = start or _now_without_microseconds() + timedelta(hours=3)
    return create_event(
        __actor=actor,
        title="Planning",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=start + timedelta(hours=1),
    )


def test_create_reminder_persists_for_actor(db):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    event = _create_event(actor)

    reminder = create_reminder(
        __actor=actor,
        event_uuid=event.uuid,
        minutes_before=60,
        method=CalendarEventReminder.Method.EMAIL,
    )

    assert reminder.pk is not None
    assert reminder.org_user_id == actor.pk
    assert reminder.minutes_before == 60
    assert reminder.method == CalendarEventReminder.Method.EMAIL
    assert reminder.original_start == event.start_time
    assert reminder.remind_at == event.start_time - timedelta(minutes=60)


def test_guest_can_set_their_own_reminder(db):
    org = test_helpers.create_org("Shared Org", save=True)["org"]
    creator = test_helpers.create_org_user(
        email="creator@law-orga.de", org=org, save=True
    )["org_user"]
    guest = test_helpers.create_org_user(email="guest@law-orga.de", org=org, save=True)[
        "org_user"
    ]
    event = _create_event(creator)
    event.grant_access(
        by=creator,
        access_level=CalendarEventShare.AccessLevel.VIEW,
        shared_user=guest,
    )

    reminder = create_reminder(
        __actor=guest,
        event_uuid=event.uuid,
        minutes_before=10,
        method=CalendarEventReminder.Method.EMAIL,
    )

    assert reminder.org_user_id == guest.pk


def test_create_reminder_rejects_user_without_access(db):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    stranger = test_helpers.create_org_user(email="stranger@law-orga.de", save=True)[
        "org_user"
    ]
    event = _create_event(actor)

    with pytest.raises(DomainError):
        create_reminder(
            __actor=stranger,
            event_uuid=event.uuid,
            minutes_before=10,
            method=CalendarEventReminder.Method.EMAIL,
        )


def test_create_reminder_rejects_exact_duplicate(db):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    event = _create_event(actor)
    create_reminder(
        __actor=actor,
        event_uuid=event.uuid,
        minutes_before=30,
        method=CalendarEventReminder.Method.EMAIL,
    )

    with pytest.raises(UseCaseError):
        create_reminder(
            __actor=actor,
            event_uuid=event.uuid,
            minutes_before=30,
            method=CalendarEventReminder.Method.EMAIL,
        )


def test_create_reminder_rejects_past_reminder_offset(db):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    event = _create_event(actor, start=timezone.now() + timedelta(minutes=10))

    with pytest.raises(UseCaseError):
        create_reminder(
            __actor=actor,
            event_uuid=event.uuid,
            minutes_before=30,
            method=CalendarEventReminder.Method.EMAIL,
        )


def test_create_event_with_reminders_creates_them(db):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    start = timezone.now() + timedelta(days=2)

    event = create_event(
        __actor=actor,
        title="Planning",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=start + timedelta(hours=1),
        reminders=["EMAIL:60", "IN_APP:1440"],
    )

    methods = set(event.reminders.values_list("method", "minutes_before"))
    assert methods == {("EMAIL", 60), ("IN_APP", 1440)}


def test_create_event_with_malformed_reminder_creates_nothing(db):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    start = timezone.now() + timedelta(days=2)

    with pytest.raises(UseCaseError):
        create_event(
            __actor=actor,
            title="Planning",
            event_type=CalendarEvent.EventType.MEETING,
            start_time=start,
            end_time=start + timedelta(hours=1),
            reminders=["EMAIL/60"],
        )

    assert CalendarEvent.objects.count() == 0


def test_create_event_with_past_reminder_creates_nothing(db):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    start = timezone.now() + timedelta(minutes=10)

    with pytest.raises(UseCaseError):
        create_event(
            __actor=actor,
            title="Planning",
            event_type=CalendarEvent.EventType.MEETING,
            start_time=start,
            end_time=start + timedelta(hours=1),
            reminders=["EMAIL:30"],
        )

    assert CalendarEvent.objects.count() == 0


def test_user_can_stack_multiple_reminders(db):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    event = _create_event(actor, start=timezone.now() + timedelta(days=2))

    create_reminder(
        __actor=actor,
        event_uuid=event.uuid,
        minutes_before=1440,
        method=CalendarEventReminder.Method.EMAIL,
    )
    create_reminder(
        __actor=actor,
        event_uuid=event.uuid,
        minutes_before=60,
        method=CalendarEventReminder.Method.EMAIL,
    )
    create_reminder(
        __actor=actor,
        event_uuid=event.uuid,
        minutes_before=60,
        method=CalendarEventReminder.Method.IN_APP,
    )

    assert event.reminders.count() == 3


def test_create_event_with_reminders_on_recurring_event(db):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    start = _now_without_microseconds() + timedelta(days=2)

    event = create_event(
        __actor=actor,
        title="Standup",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=start + timedelta(hours=1),
        recurrence_rule="FREQ=WEEKLY",
        reminders=["EMAIL:60"],
    )

    reminder = event.reminders.get()
    assert reminder.original_start == start
    assert reminder.remind_at == start - timedelta(minutes=60)


def test_create_reminder_on_recurring_event_targets_next_occurrence(db):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    # the series started three weeks ago, the next occurrence is in one week
    start = _now_without_microseconds() - timedelta(weeks=3) + timedelta(days=1)
    event = create_event(
        __actor=actor,
        title="Standup",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=start + timedelta(hours=1),
        recurrence_rule="FREQ=WEEKLY",
    )

    reminder = create_reminder(
        __actor=actor,
        event_uuid=event.uuid,
        minutes_before=60,
        method=CalendarEventReminder.Method.EMAIL,
    )

    next_slot = start + timedelta(weeks=3)
    assert reminder.original_start == next_slot
    assert reminder.remind_at == next_slot - timedelta(minutes=60)


def test_update_reminder_changes_offset_and_reschedules(db):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    start = _now_without_microseconds() + timedelta(days=2)
    event = _create_event(actor, start=start)
    reminder = create_reminder(
        __actor=actor,
        event_uuid=event.uuid,
        minutes_before=60,
        method=CalendarEventReminder.Method.EMAIL,
    )

    update_reminder(
        __actor=actor,
        reminder_uuid=reminder.uuid,
        minutes_before=30,
        method=CalendarEventReminder.Method.IN_APP,
    )

    reminder.refresh_from_db()
    assert reminder.minutes_before == 30
    assert reminder.method == CalendarEventReminder.Method.IN_APP
    assert reminder.original_start == start
    assert reminder.remind_at == start - timedelta(minutes=30)


def test_update_reminder_rejects_other_users(db):
    org = test_helpers.create_org("Shared Org", save=True)["org"]
    owner = test_helpers.create_org_user(email="owner@law-orga.de", org=org, save=True)[
        "org_user"
    ]
    other = test_helpers.create_org_user(email="other@law-orga.de", org=org, save=True)[
        "org_user"
    ]
    event = _create_event(owner)
    reminder = create_reminder(
        __actor=owner,
        event_uuid=event.uuid,
        minutes_before=60,
        method=CalendarEventReminder.Method.EMAIL,
    )

    with pytest.raises(DomainError):
        update_reminder(__actor=other, reminder_uuid=reminder.uuid, minutes_before=30)


def test_update_reminder_rejects_duplicate(db):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    event = _create_event(actor, start=timezone.now() + timedelta(days=2))
    create_reminder(
        __actor=actor,
        event_uuid=event.uuid,
        minutes_before=30,
        method=CalendarEventReminder.Method.EMAIL,
    )
    reminder = create_reminder(
        __actor=actor,
        event_uuid=event.uuid,
        minutes_before=60,
        method=CalendarEventReminder.Method.EMAIL,
    )

    with pytest.raises(UseCaseError):
        update_reminder(__actor=actor, reminder_uuid=reminder.uuid, minutes_before=30)


def test_update_reminder_rejects_past_offset(db):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    event = _create_event(actor, start=timezone.now() + timedelta(minutes=30))
    reminder = create_reminder(
        __actor=actor,
        event_uuid=event.uuid,
        minutes_before=10,
        method=CalendarEventReminder.Method.EMAIL,
    )

    with pytest.raises(UseCaseError):
        update_reminder(__actor=actor, reminder_uuid=reminder.uuid, minutes_before=60)


def test_delete_reminder_removes_own(db):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    event = _create_event(actor)
    reminder = create_reminder(
        __actor=actor,
        event_uuid=event.uuid,
        minutes_before=15,
        method=CalendarEventReminder.Method.EMAIL,
    )

    delete_reminder(__actor=actor, reminder_uuid=reminder.uuid)

    assert not CalendarEventReminder.objects.filter(pk=reminder.pk).exists()


def test_delete_reminder_rejects_other_users(db):
    org = test_helpers.create_org("Shared Org", save=True)["org"]
    owner = test_helpers.create_org_user(email="owner@law-orga.de", org=org, save=True)[
        "org_user"
    ]
    other = test_helpers.create_org_user(email="other@law-orga.de", org=org, save=True)[
        "org_user"
    ]
    event = _create_event(owner)
    reminder = create_reminder(
        __actor=owner,
        event_uuid=event.uuid,
        minutes_before=15,
        method=CalendarEventReminder.Method.EMAIL,
    )

    with pytest.raises(DomainError):
        delete_reminder(__actor=other, reminder_uuid=reminder.uuid)


def test_moving_start_time_reschedules_reminders(db):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    start = _now_without_microseconds() + timedelta(hours=3)
    event = _create_event(actor, start=start)
    reminder = create_reminder(
        __actor=actor,
        event_uuid=event.uuid,
        minutes_before=60,
        method=CalendarEventReminder.Method.EMAIL,
    )
    # simulate that the reminder already fired for the old time
    reminder.original_start = None
    reminder.remind_at = None
    reminder.save(update_fields=["original_start", "remind_at"])

    new_start = start + timedelta(days=1)
    update_event(
        __actor=actor,
        event_uuid=event.uuid,
        start_time=new_start,
        end_time=new_start + timedelta(hours=1),
    )

    reminder.refresh_from_db()
    assert reminder.original_start == new_start
    assert reminder.remind_at == new_start - timedelta(minutes=60)


def test_editing_without_moving_start_keeps_reminder_dispatched(db):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    start = _now_without_microseconds() + timedelta(minutes=20)
    event = _create_event(actor, start=start)
    reminder = CalendarEventReminder.create(
        event=event,
        org_user=actor,
        minutes_before=60,
        method=CalendarEventReminder.Method.EMAIL,
        original_start=start,
        remind_at=start - timedelta(minutes=60),
    )
    reminder.original_start = None
    reminder.remind_at = None
    reminder.save()

    update_event(
        __actor=actor,
        event_uuid=event.uuid,
        title="Renamed",
        start_time=start,
    )

    reminder.refresh_from_db()
    assert reminder.remind_at is None
    assert reminder.original_start is None
