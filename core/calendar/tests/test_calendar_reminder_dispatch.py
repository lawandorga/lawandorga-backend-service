from datetime import timedelta

from django.utils import timezone

from core.calendar.models import (
    CalendarEvent,
    CalendarEventReminder,
    CalendarNotification,
)
from core.calendar.reminders import send_due_reminders
from core.tests import test_helpers


def _create_event(actor, *, start, location="", description=""):
    return CalendarEvent.create(
        creator=actor,
        title="Court date",
        event_type=CalendarEvent.EventType.APPOINTMENT,
        start_time=start,
        end_time=start + timedelta(hours=1),
        location=location,
        description=description,
    )


def _add_reminder(event, actor, *, minutes_before, method):
    reminder = CalendarEventReminder.create(
        event=event,
        org_user=actor,
        minutes_before=minutes_before,
        method=method,
    )
    reminder.save()
    return reminder


def test_due_email_reminder_is_sent_once(db, mailoutbox):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    event = _create_event(
        actor,
        start=timezone.now() + timedelta(minutes=20),
        location="Room 5",
        description="Bring the documents",
    )
    event.save()
    reminder = _add_reminder(
        event, actor, minutes_before=30, method=CalendarEventReminder.Method.EMAIL
    )

    send_due_reminders()

    assert len(mailoutbox) == 1
    assert actor.email in mailoutbox[0].to
    assert "in 30 minutes" in mailoutbox[0].body
    assert "Room 5" in mailoutbox[0].body
    assert "Bring the documents" in mailoutbox[0].body
    reminder.refresh_from_db()
    assert reminder.dispatched_at is not None

    # A second run must not send the same reminder again.
    send_due_reminders()
    assert len(mailoutbox) == 1


def test_reminder_not_yet_due_is_not_sent(db, mailoutbox):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    event = _create_event(actor, start=timezone.now() + timedelta(hours=2))
    event.save()
    reminder = _add_reminder(
        event, actor, minutes_before=30, method=CalendarEventReminder.Method.EMAIL
    )

    send_due_reminders()

    assert len(mailoutbox) == 0
    reminder.refresh_from_db()
    assert reminder.dispatched_at is None


def test_due_in_app_reminder_creates_notification(db, mailoutbox):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    event = _create_event(actor, start=timezone.now() + timedelta(minutes=20))
    event.save()
    reminder = _add_reminder(
        event, actor, minutes_before=30, method=CalendarEventReminder.Method.IN_APP
    )

    send_due_reminders()

    assert len(mailoutbox) == 0  # in-app, not email
    assert CalendarNotification.objects.filter(org_user=actor, event=event).count() == 1
    reminder.refresh_from_db()
    assert reminder.dispatched_at is not None

    # A second run must not create a duplicate notification.
    send_due_reminders()
    assert CalendarNotification.objects.filter(org_user=actor, event=event).count() == 1
