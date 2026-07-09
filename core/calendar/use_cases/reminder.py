from datetime import timedelta
from uuid import UUID

from django.utils import timezone

from core.auth.models.org_user import OrgUser
from core.calendar.models import CalendarEvent, CalendarEventReminder
from core.seedwork.domain_layer import DomainError
from core.seedwork.use_case_layer import use_case
from core.seedwork.use_case_layer.error import UseCaseError


@use_case
def create_reminder(
    __actor: OrgUser,
    event_uuid: UUID,
    minutes_before: int,
    method: CalendarEventReminder.Method,
) -> CalendarEventReminder:
    event = CalendarEvent.objects.get(uuid=event_uuid)

    if not event.has_view_access(__actor):
        raise DomainError("You can only set reminders on events you can access.")

    already_exists = CalendarEventReminder.objects.filter(
        event=event,
        org_user=__actor,
        method=method,
        minutes_before=minutes_before,
    ).exists()
    if already_exists:
        raise UseCaseError("You already have an identical reminder for this event.")

    now = timezone.now()
    if event.start_time < now or event.start_time - timedelta(minutes=minutes_before) < now:
        raise UseCaseError("You cannot set a reminder in the past.")

    reminder = CalendarEventReminder.create(
        event=event,
        org_user=__actor,
        minutes_before=minutes_before,
        method=method,
    )
    reminder.save()
    return reminder


@use_case
def delete_reminder(
    __actor: OrgUser,
    reminder_uuid: UUID,
) -> None:
    reminder = CalendarEventReminder.objects.get(uuid=reminder_uuid)

    if reminder.org_user_id != __actor.pk:
        raise DomainError("You can only delete your own reminders.")

    reminder.delete()
