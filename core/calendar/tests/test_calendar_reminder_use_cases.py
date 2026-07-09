from datetime import timedelta

import pytest
from django.utils import timezone

from core.calendar.models import (
    CalendarEvent,
    CalendarEventReminder,
    CalendarEventShare,
)
from core.calendar.use_cases.event import create_event, update_event
from core.calendar.use_cases.reminder import create_reminder, delete_reminder
from core.seedwork.domain_layer import DomainError
from core.seedwork.use_case_layer.error import UseCaseError
from core.tests import test_helpers


def _create_event(actor, start=None):
    start = start or timezone.now() + timedelta(hours=3)
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
    assert reminder.remind_at == event.start_time - timedelta(minutes=60)
    assert reminder.dispatched_at is None


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


def test_user_can_stack_multiple_reminders(db):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    event = _create_event(actor)

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
        method=CalendarEventReminder.Method.PUSH,
    )

    assert event.reminders.count() == 3


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
    start = timezone.now() + timedelta(hours=3)
    event = _create_event(actor, start=start)
    reminder = create_reminder(
        __actor=actor,
        event_uuid=event.uuid,
        minutes_before=60,
        method=CalendarEventReminder.Method.EMAIL,
    )
    reminder.dispatched_at = timezone.now()
    reminder.save(update_fields=["dispatched_at"])

    new_start = start + timedelta(days=1)
    update_event(
        __actor=actor,
        event_uuid=event.uuid,
        start_time=new_start,
        end_time=new_start + timedelta(hours=1),
    )

    reminder.refresh_from_db()
    assert reminder.remind_at == new_start - timedelta(minutes=60)
    assert reminder.dispatched_at is None


def test_editing_without_moving_start_keeps_reminder_dispatched(db):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    start = timezone.now() + timedelta(hours=3)
    event = _create_event(actor, start=start)
    reminder = create_reminder(
        __actor=actor,
        event_uuid=event.uuid,
        minutes_before=60,
        method=CalendarEventReminder.Method.EMAIL,
    )
    dispatched_at = timezone.now()
    reminder.dispatched_at = dispatched_at
    reminder.save(update_fields=["dispatched_at"])

    # The frontend resends start_time on every edit; a title-only change must
    # not re-arm an already-sent reminder.
    update_event(
        __actor=actor,
        event_uuid=event.uuid,
        title="Renamed",
        start_time=start,
    )

    reminder.refresh_from_db()
    assert reminder.dispatched_at == dispatched_at
