from datetime import date, datetime
from uuid import UUID

from django.db.models import Prefetch
from django.utils import timezone
from pydantic import BaseModel, ConfigDict

from core.auth.models import OrgUser
from core.calendar.models.event import (
    CalendarEvent,
    CalendarEventOccurrenceOverride,
    CalendarEventReminder,
    CalendarNotification,
)
from core.calendar.occurrences import get_occurrences
from core.seedwork.api_layer import Router

router = Router()


class OutputCalendarEventReminder(BaseModel):
    uuid: UUID
    minutes_before: int
    method: str

    model_config = ConfigDict(from_attributes=True)


class OutputOccurrenceOverride(BaseModel):
    uuid: UUID
    original_start: datetime
    cancelled: bool
    start_time: datetime | None
    end_time: datetime | None
    title: str | None
    description: str | None
    location: str | None

    model_config = ConfigDict(from_attributes=True)


class OutputCalendarEvent(BaseModel):
    uuid: UUID
    creator_id: int
    creator_name: str
    title: str
    description: str
    event_type: str
    start_time: datetime
    end_time: datetime | None
    is_all_day: bool
    location: str
    recurrence_rule: str
    recurrence_until: date | None
    grant_targets: list[str]
    guest_user_ids: list[int]
    guest_user_names: list[str]
    own_reminders: list[OutputCalendarEventReminder]
    overrides: list[OutputOccurrenceOverride]
    created: datetime
    updated: datetime

    model_config = ConfigDict(from_attributes=True)


@router.get(
    url="events/",
    output_schema=list[OutputCalendarEvent],
)
def query__calendar_events(org_user: OrgUser):
    own_reminders = CalendarEventReminder.objects.filter(org_user=org_user)
    return (
        CalendarEvent.get_accessible_events_for_user(org_user)
        .select_related("creator", "creator__user")
        .prefetch_related(
            "shares",
            "shares__shared_user",
            "shares__shared_user__user",
            Prefetch(
                "occurrence_overrides",
                queryset=CalendarEventOccurrenceOverride.objects.all(),
                to_attr="overrides",
            ),
            Prefetch("reminders", queryset=own_reminders, to_attr="own_reminders"),
        )
    )


class InputCalendarOccurrences(BaseModel):
    from_dt: datetime
    to_dt: datetime


class OutputOccurrence(BaseModel):
    event_uuid: UUID
    original_start: datetime
    title: str
    start_time: datetime
    end_time: datetime
    is_all_day: bool
    event_type: str


@router.get(
    url="occurrences/",
    output_schema=list[OutputOccurrence],
)
def query__calendar_occurrences(org_user: OrgUser, data: InputCalendarOccurrences):
    events = CalendarEvent.get_accessible_events_for_user(org_user).prefetch_related(
        "occurrence_overrides"
    )
    return [
        OutputOccurrence(
            event_uuid=event.uuid,
            original_start=occurrence.original_start,
            title=occurrence.title,
            start_time=occurrence.start_time,
            end_time=occurrence.end_time,
            is_all_day=event.is_all_day,
            event_type=event.event_type,
        )
        for event in events
        for occurrence in get_occurrences(event, from_dt=data.from_dt, to_dt=data.to_dt)
    ]


class OutputCalendarNotification(BaseModel):
    uuid: UUID
    message: str
    event_uuid: UUID
    read_at: datetime | None
    created: datetime

    model_config = ConfigDict(from_attributes=True)


@router.get(
    url="notifications/",
    output_schema=list[OutputCalendarNotification],
)
def query__notifications(org_user: OrgUser):
    now = timezone.now()
    return CalendarNotification.objects.filter(
        org_user=org_user, occurrence_end__gte=now
    ).select_related("event")
