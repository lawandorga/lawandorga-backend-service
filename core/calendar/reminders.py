import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template import loader
from django.utils import timezone

from core.calendar.models import CalendarEventReminder

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


def send_due_reminders() -> str:
    now = timezone.now()
    due_reminders = CalendarEventReminder.objects.filter(
        remind_at__lte=now,
        dispatched_at__isnull=True,
        method=CalendarEventReminder.Method.EMAIL,
        # Recurring events will be handled later
        event__recurrence_rule="",
    ).select_related("event", "org_user", "org_user__user")

    sent = 0
    failed = 0
    for reminder in due_reminders:
        try:
            _send_reminder_email(reminder)
        except Exception:
            logger.warning(
                "Failed to send calendar reminder %s", reminder.uuid, exc_info=True
            )
            failed += 1
            continue
        reminder.dispatched_at = now
        reminder.save(update_fields=["dispatched_at"])
        sent += 1

    return f"Sent {_pluralize(sent, 'calendar reminder')}, {failed} failed."
