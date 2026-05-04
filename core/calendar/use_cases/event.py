from datetime import date, datetime
from uuid import UUID

from core.auth.models.org_user import OrgUser
from core.calendar.models import CalendarEvent, RecurrenceRule
from core.seedwork.domain_layer import DomainError
from core.seedwork.use_case_layer import use_case


@use_case
def create_event(
    __actor: OrgUser,
    title: str,
    event_type: CalendarEvent.EventType,
    start_time: datetime,
    end_time: datetime | None = None,
    description: str | None = None,
    location: str | None = None,
    recurrence_rule: str | None = None,
    recurrence_until: date | None = None,
) -> CalendarEvent:
    event = CalendarEvent.create(
        creator=__actor,
        title=title,
        event_type=event_type,
        start_time=start_time,
        end_time=end_time,
        description=description or "",
        location=location or "",
        recurrence_rule=RecurrenceRule.create(recurrence_rule),
        recurrence_until=recurrence_until,
    )
    event.save()
    return event


@use_case
def update_event(
    __actor: OrgUser,
    event_uuid: UUID,
    title: str | None = None,
    description: str | None = None,
    event_type: CalendarEvent.EventType | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    location: str | None = None,
    recurrence_rule: str | None = None,
    recurrence_until: date | None = None,
) -> CalendarEvent:
    event = CalendarEvent.objects.get(uuid=event_uuid)
    if event.creator != __actor:
        raise DomainError("You can only edit your own events.")
    event.update_information(
        title=title,
        description=description,
        event_type=event_type,
        start_time=start_time,
        end_time=end_time,
        location=location,
        recurrence_rule=(
            RecurrenceRule.create(recurrence_rule)
            if recurrence_rule is not None
            else None
        ),
        recurrence_until=recurrence_until,
    )
    event.save()
    return event


@use_case
def delete_event(
    __actor: OrgUser,
    event_uuid: UUID,
) -> None:
    event = CalendarEvent.objects.get(uuid=event_uuid)
    if event.creator != __actor:
        raise DomainError("You can only delete your own events.")
    event.delete()
