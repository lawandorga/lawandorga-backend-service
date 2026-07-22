from datetime import timedelta

from django.utils import timezone

from core.calendar.models import (
    CalendarEvent,
    CalendarEventOccurrenceOverride,
    CalendarEventReminder,
    CalendarNotification,
    RecurrenceRule,
)
from core.calendar.reminders import dispatch_due_reminders
from core.tests import test_helpers


def _create_event(actor, *, start, rule="", location="", description=""):
    event = CalendarEvent.create(
        creator=actor,
        title="Court date",
        event_type=CalendarEvent.EventType.APPOINTMENT,
        start_time=start,
        end_time=start + timedelta(hours=1),
        recurrence_rule=RecurrenceRule.create(rule or None),
        location=location,
        description=description,
    )
    event.save()
    return event


def _add_due_reminder(event, actor, *, minutes_before, method, original_start=None):
    original_start = original_start if original_start is not None else event.start_time
    reminder = CalendarEventReminder.create(
        event=event,
        org_user=actor,
        minutes_before=minutes_before,
        method=method,
        original_start=original_start,
        remind_at=timezone.now() - timedelta(minutes=1),
    )
    reminder.save()
    return reminder


def _actor():
    return test_helpers.create_org_user(save=True)["org_user"]


def _now_without_microseconds():
    # dateutil expands recurrences with second precision
    return timezone.now().replace(microsecond=0)


def test_due_email_reminder_is_sent_once(db, mailoutbox):
    actor = _actor()
    event = _create_event(
        actor,
        start=_now_without_microseconds() + timedelta(minutes=20),
        location="Room 5",
        description="Bring the documents",
    )
    reminder = _add_due_reminder(
        event, actor, minutes_before=30, method=CalendarEventReminder.Method.EMAIL
    )

    result = dispatch_due_reminders()

    assert len(mailoutbox) == 1
    assert actor.email in mailoutbox[0].to
    assert "in 30 minutes" in mailoutbox[0].body
    assert "Room 5" in mailoutbox[0].body
    assert "Bring the documents" in mailoutbox[0].body
    assert "Email: 1 sent, 0 failed" in result
    reminder.refresh_from_db()
    assert reminder.remind_at is None
    assert reminder.original_start is None

    # A second run must not send the same reminder again.
    dispatch_due_reminders()
    assert len(mailoutbox) == 1


def test_reminder_not_yet_due_is_not_sent(db, mailoutbox):
    actor = _actor()
    event = _create_event(actor, start=_now_without_microseconds() + timedelta(hours=2))
    reminder = CalendarEventReminder.create(
        event=event,
        org_user=actor,
        minutes_before=30,
        method=CalendarEventReminder.Method.EMAIL,
        original_start=event.start_time,
        remind_at=event.start_time - timedelta(minutes=30),
    )
    reminder.save()

    dispatch_due_reminders()

    assert len(mailoutbox) == 0
    reminder.refresh_from_db()
    assert reminder.remind_at == event.start_time - timedelta(minutes=30)


def test_due_in_app_reminder_creates_notification(db, mailoutbox):
    actor = _actor()
    event = _create_event(
        actor, start=_now_without_microseconds() + timedelta(minutes=20)
    )
    reminder = _add_due_reminder(
        event, actor, minutes_before=30, method=CalendarEventReminder.Method.IN_APP
    )

    result = dispatch_due_reminders()

    assert len(mailoutbox) == 0  # in-app, not email
    notification = CalendarNotification.objects.get(org_user=actor, event=event)
    assert notification.occurrence_end == event.end_time
    assert "In-app: 1 created, 0 failed" in result
    reminder.refresh_from_db()
    assert reminder.remind_at is None

    # A second run must not create a duplicate notification.
    dispatch_due_reminders()
    assert CalendarNotification.objects.filter(org_user=actor, event=event).count() == 1


def test_recurring_reminder_fires_and_advances_to_next_occurrence(db, mailoutbox):
    actor = _actor()
    # a daily series that started 23h ago, so its next slot is one hour from now
    base = _now_without_microseconds() - timedelta(hours=23)
    event = _create_event(actor, start=base, rule="FREQ=DAILY")
    upcoming_slot = base + timedelta(days=1)
    reminder = _add_due_reminder(
        event,
        actor,
        minutes_before=90,
        method=CalendarEventReminder.Method.EMAIL,
        original_start=upcoming_slot,
    )

    dispatch_due_reminders()

    assert len(mailoutbox) == 1
    reminder.refresh_from_db()
    assert reminder.original_start == upcoming_slot + timedelta(days=1)
    assert reminder.remind_at == reminder.original_start - timedelta(minutes=90)

    # The next run has nothing due for this reminder anymore.
    dispatch_due_reminders()
    assert len(mailoutbox) == 1


def test_reminder_for_cancelled_occurrence_skips_and_advances(db, mailoutbox):
    actor = _actor()
    base = _now_without_microseconds() - timedelta(hours=23)
    event = _create_event(actor, start=base, rule="FREQ=DAILY")
    upcoming_slot = base + timedelta(days=1)
    CalendarEventOccurrenceOverride.objects.create(
        event=event, original_start=upcoming_slot, cancelled=True
    )
    reminder = _add_due_reminder(
        event,
        actor,
        minutes_before=90,
        method=CalendarEventReminder.Method.EMAIL,
        original_start=upcoming_slot,
    )

    dispatch_due_reminders()

    assert len(mailoutbox) == 0
    reminder.refresh_from_db()
    assert reminder.original_start == upcoming_slot + timedelta(days=1)


def test_reminder_for_moved_occurrence_uses_moved_time(db, mailoutbox):
    actor = _actor()
    base = _now_without_microseconds() - timedelta(hours=23)
    event = _create_event(actor, start=base, rule="FREQ=DAILY")
    upcoming_slot = base + timedelta(days=1)
    moved_start = upcoming_slot + timedelta(hours=2)
    CalendarEventOccurrenceOverride.objects.create(
        event=event,
        original_start=upcoming_slot,
        start_time=moved_start,
        title="Court date (moved)",
    )
    reminder = _add_due_reminder(
        event,
        actor,
        minutes_before=240,
        method=CalendarEventReminder.Method.IN_APP,
        original_start=upcoming_slot,
    )

    dispatch_due_reminders()

    notification = CalendarNotification.objects.get(org_user=actor)
    assert "Court date (moved)" in notification.message
    moved_local = timezone.localtime(moved_start).strftime("%Y-%m-%d %H:%M")
    assert moved_local in notification.message
    reminder.refresh_from_db()
    assert reminder.original_start == upcoming_slot + timedelta(days=1)


def test_missed_occurrence_is_skipped_without_sending(db, mailoutbox):
    actor = _actor()
    # The occurrence already started (e.g. the cron failed)
    event = _create_event(
        actor, start=_now_without_microseconds() - timedelta(minutes=10)
    )
    reminder = _add_due_reminder(
        event, actor, minutes_before=30, method=CalendarEventReminder.Method.EMAIL
    )

    dispatch_due_reminders()

    assert len(mailoutbox) == 0
    reminder.refresh_from_db()
    assert reminder.remind_at is None
    assert reminder.original_start is None
