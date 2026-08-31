import logging
from collections import Counter
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import NamedTuple, TypeGuard
from urllib.parse import urlencode

from django.conf import settings
from django.core.mail import send_mail
from django.template import loader
from django.utils import timezone

from core.calendar.models import (
    CalendarEvent,
    CalendarEventReminder,
    CalendarNotification,
)
from core.calendar.occurrences import (
    Occurrence,
    get_next_occurrence,
    get_occurrence,
)

logger = logging.getLogger("django")


def _pluralize(value: int, unit: str) -> str:
    return f"{value} {unit}" if value == 1 else f"{value} {unit}s"


def _lead_time_label(minutes_before: int) -> str:
    if minutes_before == 0:
        return "now"

    days, remainder = divmod(minutes_before, 60 * 24)
    hours, minutes = divmod(remainder, 60)
    parts = []
    if days:
        parts.append(_pluralize(days, "day"))
    if hours:
        parts.append(_pluralize(hours, "hour"))
    if minutes:
        parts.append(_pluralize(minutes, "minute"))
    return "in " + " ".join(parts)


class ReminderSchedule(NamedTuple):
    original_start: datetime
    remind_at: datetime


def compute_reminder_schedule(
    event: CalendarEvent, minutes_before: int, *, after: datetime
) -> ReminderSchedule | None:
    offset = timedelta(minutes=minutes_before)
    # the reminder itself must be in the future, so its occurrence has to
    # start at least one lead time after `after`
    occurrence = get_next_occurrence(event, after=after + offset)
    if occurrence is None:
        return None
    return ReminderSchedule(occurrence.original_start, occurrence.start_time - offset)


def _apply_schedule(
    reminder: CalendarEventReminder, schedule: ReminderSchedule | None
) -> None:
    if schedule is None:
        reminder.original_start = None
        reminder.remind_at = None
    else:
        reminder.original_start, reminder.remind_at = schedule


def resync_event_reminders(event: CalendarEvent) -> None:
    now = timezone.now()
    reminders = list(event.reminders.all())
    # reminders sharing a lead time share a schedule, and each one walks the series
    schedule_by_minutes_before: dict[int, ReminderSchedule | None] = {}

    for reminder in reminders:
        if reminder.minutes_before not in schedule_by_minutes_before:
            schedule_by_minutes_before[reminder.minutes_before] = (
                compute_reminder_schedule(event, reminder.minutes_before, after=now)
            )
        _apply_schedule(reminder, schedule_by_minutes_before[reminder.minutes_before])

    CalendarEventReminder.objects.bulk_update(
        reminders, ["original_start", "remind_at"]
    )


class OccurrenceLabels(NamedTuple):
    lead_time: str
    formatted_start: str


def _occurrence_labels(
    reminder: CalendarEventReminder, occurrence: Occurrence
) -> OccurrenceLabels:
    local_start = timezone.localtime(occurrence.start_time)
    return OccurrenceLabels(
        lead_time=_lead_time_label(reminder.minutes_before),
        formatted_start=local_start.strftime("%Y-%m-%d %H:%M %Z"),
    )


def _send_reminder_email(
    reminder: CalendarEventReminder, occurrence: Occurrence
) -> None:
    lead_time, formatted_start = _occurrence_labels(reminder, occurrence)

    query = {"event": str(reminder.event.uuid)}
    if reminder.event.recurrence_rule:
        query["start"] = occurrence.original_start.isoformat()
    event_url = f"{settings.MAIN_FRONTEND_URL}/calendar/?{urlencode(query)}"

    context = {
        "user_name": reminder.org_user.name,
        "occurrence": occurrence,
        "start_time": formatted_start,
        "lead_time": lead_time,
        "event_url": event_url,
    }
    subject = f"Law&Orga reminder: {occurrence.title}"
    details = ""
    if occurrence.location:
        details += f"Location: {occurrence.location}\n"
    if occurrence.description:
        details += f"{occurrence.description}\n"
    if details:
        details += "\n"
    message = (
        f"Dear {reminder.org_user.name},\n\n"
        f'This is a reminder for "{occurrence.title}", starting {lead_time} '
        f"at {formatted_start}.\n\n"
        f"{details}"
        f"Open the event: {event_url}\n\n"
        "Best regards,\nThe Law&Orga Team"
    )
    html_message = loader.render_to_string(
        "email_templates/calendar_reminder.html", context
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[reminder.org_user.email],
        html_message=html_message,
    )


def _create_reminder_notification(
    reminder: CalendarEventReminder, occurrence: Occurrence
) -> None:
    lead_time, formatted_start = _occurrence_labels(reminder, occurrence)
    CalendarNotification.objects.create(
        org_user=reminder.org_user,
        event=reminder.event,
        message=f'"{occurrence.title}" starts {lead_time} at {formatted_start}.',
        occurrence_end=occurrence.end_time,
    )


_EMAIL = CalendarEventReminder.Method.EMAIL
_IN_APP = CalendarEventReminder.Method.IN_APP

_DELIVER_BY_METHOD: dict[str, Callable[[CalendarEventReminder, Occurrence], None]] = {
    _EMAIL: _send_reminder_email,
    _IN_APP: _create_reminder_notification,
}


def _should_send_reminder(
    occurrence: Occurrence | None, now: datetime
) -> TypeGuard[Occurrence]:
    return (
        occurrence is not None
        and not occurrence.cancelled
        and occurrence.end_time > now
    )


def _advance_schedule(reminder: CalendarEventReminder, after: datetime) -> None:
    schedule = compute_reminder_schedule(
        reminder.event, reminder.minutes_before, after=after
    )
    _apply_schedule(reminder, schedule)
    reminder.save(update_fields=["original_start", "remind_at"])


def dispatch_due_reminders() -> str:
    now = timezone.now()
    due_reminders = (
        CalendarEventReminder.objects.filter(
            remind_at__isnull=False,
            remind_at__lte=now,
        ).select_related("event", "org_user", "org_user__user")
        # every occurrence lookup below reads the event's overrides
        .prefetch_related("event__occurrence_overrides")
    )

    dispatched: Counter[str] = Counter()
    failed: Counter[str] = Counter()
    for reminder in due_reminders:
        try:
            occurrence = None
            if reminder.original_start is not None:
                occurrence = get_occurrence(reminder.event, reminder.original_start)
            if _should_send_reminder(occurrence, now):
                _DELIVER_BY_METHOD[reminder.method](reminder, occurrence)
                dispatched[reminder.method] += 1
                advance_after = occurrence.start_time
            else:
                advance_after = now
            _advance_schedule(reminder, advance_after)
        except Exception:
            # The schedule is left untouched, so the next run retries.
            logger.warning(
                "Failed to dispatch calendar reminder %s", reminder.uuid, exc_info=True
            )
            failed[reminder.method] += 1

    return (
        f"Dispatched {_pluralize(sum(dispatched.values()), 'calendar reminder')}, "
        f"{sum(failed.values())} failed.\n"
        f"Email: {dispatched[_EMAIL]} sent, {failed[_EMAIL]} failed.\n"
        f"In-app: {dispatched[_IN_APP]} created, {failed[_IN_APP]} failed."
    )
