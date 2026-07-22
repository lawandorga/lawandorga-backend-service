from datetime import datetime
from uuid import UUID

from core.auth.models.org_user import OrgUser
from core.calendar.models import CalendarEvent, CalendarEventOccurrenceOverride
from core.calendar.occurrences import ensure_aware, normalize_slot, series_contains_slot
from core.calendar.reminders import resync_event_reminders
from core.seedwork.domain_layer import DomainError
from core.seedwork.use_case_layer import use_case
from core.seedwork.use_case_layer.error import UseCaseError


def _get_event_for_occurrence_edit(
    actor: OrgUser, event_uuid: UUID, original_start: datetime
) -> CalendarEvent:
    event = CalendarEvent.objects.get(uuid=event_uuid)

    if not event.has_edit_access(actor):
        raise DomainError("You can only edit events with edit access.")
    if not event.recurrence_rule:
        raise UseCaseError("Only repeating events have single occurrences.")
    if not series_contains_slot(event, original_start):
        raise UseCaseError("This is not an occurrence of the event.")

    return event


@use_case
def update_event_occurrence(
    __actor: OrgUser,
    event_uuid: UUID,
    original_start: datetime,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    title: str | None = None,
    description: str | None = None,
    location: str | None = None,
) -> CalendarEventOccurrenceOverride:
    original_start = normalize_slot(ensure_aware(original_start))
    event = _get_event_for_occurrence_edit(__actor, event_uuid, original_start)

    override = CalendarEventOccurrenceOverride.objects.filter(
        event=event, original_start=original_start
    ).first()

    new_start = override.start_time if override is not None else None
    if start_time is not None:
        new_start = ensure_aware(start_time)
    new_end = override.end_time if override is not None else None
    if end_time is not None:
        new_end = ensure_aware(end_time)

    duration = event.end_time - event.start_time
    effective_start = new_start if new_start is not None else original_start
    effective_end = new_end if new_end is not None else effective_start + duration
    if effective_start > effective_end:
        raise DomainError("The start time must be before the end time.")

    if override is None:
        override = CalendarEventOccurrenceOverride(
            event=event, original_start=original_start
        )
    override.start_time = new_start
    override.end_time = new_end
    if title is not None:
        override.title = title
    if description is not None:
        override.description = description
    if location is not None:
        override.location = location

    override.save()
    resync_event_reminders(event)
    return override


@use_case
def cancel_event_occurrence(
    __actor: OrgUser,
    event_uuid: UUID,
    original_start: datetime,
) -> None:
    original_start = normalize_slot(ensure_aware(original_start))
    event = _get_event_for_occurrence_edit(__actor, event_uuid, original_start)

    override, _ = CalendarEventOccurrenceOverride.objects.get_or_create(
        event=event, original_start=original_start
    )
    override.cancelled = True
    override.save(update_fields=["cancelled", "updated"])
    resync_event_reminders(event)
