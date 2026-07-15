from datetime import datetime, timedelta
from uuid import UUID

from django.utils import timezone

from core.auth.models.org_user import OrgUser
from core.calendar.models import CalendarEvent, CalendarEventReminder
from core.seedwork.domain_layer import DomainError
from core.seedwork.use_case_layer import use_case
from core.seedwork.use_case_layer.error import UseCaseError


def parse_reminder(raw: str) -> tuple[CalendarEventReminder.Method, int]:
    raw_method, _, raw_minutes = raw.partition(":")
    try:
        method = CalendarEventReminder.Method(raw_method)
        minutes_before = int(raw_minutes)
    except ValueError as exc:
        raise UseCaseError("Reminders are malformed.") from exc
    if minutes_before < 0:
        raise UseCaseError("Reminders are malformed.")
    return method, minutes_before


def ensure_reminder_is_in_future(start_time: datetime, minutes_before: int) -> None:
    # The frontend sends local datetimes without timezone
    if timezone.is_naive(start_time):
        start_time = timezone.make_aware(start_time)
    now = timezone.now()
    if start_time < now or start_time - timedelta(minutes=minutes_before) < now:
        raise UseCaseError("You cannot set a reminder in the past.")


def save_new_reminder(
    *,
    event: CalendarEvent,
    org_user: OrgUser,
    minutes_before: int,
    method: CalendarEventReminder.Method,
) -> CalendarEventReminder:
    already_exists = CalendarEventReminder.objects.filter(
        event=event,
        org_user=org_user,
        method=method,
        minutes_before=minutes_before,
    ).exists()
    if already_exists:
        raise UseCaseError("You already have an identical reminder for this event.")

    ensure_reminder_is_in_future(event.start_time, minutes_before)

    reminder = CalendarEventReminder.create(
        event=event,
        org_user=org_user,
        minutes_before=minutes_before,
        method=method,
    )
    reminder.save()
    return reminder


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

    return save_new_reminder(
        event=event,
        org_user=__actor,
        minutes_before=minutes_before,
        method=method,
    )


@use_case
def update_reminder(
    __actor: OrgUser,
    reminder_uuid: UUID,
    minutes_before: int | None = None,
    method: CalendarEventReminder.Method | None = None,
) -> CalendarEventReminder:
    reminder = CalendarEventReminder.objects.select_related("event").get(
        uuid=reminder_uuid
    )

    if reminder.org_user_id != __actor.pk:
        raise DomainError("You can only change your own reminders.")

    new_minutes = (
        minutes_before if minutes_before is not None else reminder.minutes_before
    )
    new_method = method if method is not None else reminder.method

    if new_minutes < 0:
        raise UseCaseError("Reminders are malformed.")

    duplicate_exists = (
        CalendarEventReminder.objects.filter(
            event=reminder.event,
            org_user=__actor,
            method=new_method,
            minutes_before=new_minutes,
        )
        .exclude(pk=reminder.pk)
        .exists()
    )
    if duplicate_exists:
        raise UseCaseError("You already have an identical reminder for this event.")

    ensure_reminder_is_in_future(reminder.event.start_time, new_minutes)

    reminder.minutes_before = new_minutes
    reminder.method = new_method
    reminder.remind_at = CalendarEventReminder.compute_remind_at(
        reminder.event.start_time, new_minutes
    )
    reminder.dispatched_at = None
    reminder.save(
        update_fields=["minutes_before", "method", "remind_at", "dispatched_at"]
    )
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
