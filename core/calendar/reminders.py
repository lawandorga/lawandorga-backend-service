import logging
from collections import Counter
from collections.abc import Callable

from django.conf import settings
from django.core.mail import send_mail
from django.template import loader
from django.utils import timezone

from core.calendar.models import CalendarEventReminder, CalendarNotification

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


def _send_reminder_email(reminder: CalendarEventReminder) -> None:
    event = reminder.event
    lead_time = _lead_time_label(reminder.minutes_before)
    start = timezone.localtime(event.start_time).strftime("%Y-%m-%d %H:%M %Z")
    context = {
        "user_name": reminder.org_user.name,
        "event": event,
        "start_time": start,
        "lead_time": lead_time,
        "calendar_url": f"{settings.MAIN_FRONTEND_URL}/calendar/",
    }
    subject = f"Law&Orga reminder: {event.title}"
    details = ""
    if event.location:
        details += f"Location: {event.location}\n"
    if event.description:
        details += f"{event.description}\n"
    if details:
        details += "\n"
    message = (
        f"Dear {reminder.org_user.name},\n\n"
        f'This is a reminder for "{event.title}", starting {lead_time} '
        f"at {start}.\n\n"
        f"{details}"
        f"Open your calendar: {context['calendar_url']}\n\n"
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


def _create_reminder_notification(reminder: CalendarEventReminder) -> None:
    event = reminder.event
    lead_time = _lead_time_label(reminder.minutes_before)
    start = timezone.localtime(event.start_time).strftime("%Y-%m-%d %H:%M %Z")
    CalendarNotification.objects.create(
        org_user=reminder.org_user,
        event=event,
        message=f'"{event.title}" starts {lead_time} at {start}.',
    )


_EMAIL = CalendarEventReminder.Method.EMAIL
_IN_APP = CalendarEventReminder.Method.IN_APP

_DELIVER_BY_METHOD: dict[str, Callable[[CalendarEventReminder], None]] = {
    _EMAIL: _send_reminder_email,
    _IN_APP: _create_reminder_notification,
}


def _dispatch_reminder(reminder: CalendarEventReminder) -> None:
    deliver = _DELIVER_BY_METHOD.get(reminder.method)
    if deliver is None:
        raise ValueError(f"Unhandled reminder method: {reminder.method}")
    deliver(reminder)


def send_due_reminders() -> str:
    now = timezone.now()
    due_reminders = CalendarEventReminder.objects.filter(
        remind_at__lte=now,
        dispatched_at__isnull=True,
        # Recurring events will be handled later
        event__recurrence_rule="",
    ).select_related("event", "org_user", "org_user__user")

    sent: Counter[str] = Counter()
    failed: Counter[str] = Counter()
    for reminder in due_reminders:
        try:
            _dispatch_reminder(reminder)
        except Exception:
            logger.warning(
                "Failed to dispatch calendar reminder %s", reminder.uuid, exc_info=True
            )
            failed[reminder.method] += 1
            continue
        reminder.dispatched_at = now
        reminder.save(update_fields=["dispatched_at"])
        sent[reminder.method] += 1

    return (
        f"Dispatched {_pluralize(sum(sent.values()), 'calendar reminder')}, "
        f"{sum(failed.values())} failed.\n"
        f"Email: {sent[_EMAIL]} sent, {failed[_EMAIL]} failed.\n"
        f"In-app: {sent[_IN_APP]} created, {failed[_IN_APP]} failed."
    )
