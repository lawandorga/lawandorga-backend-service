from datetime import date, datetime
from uuid import UUID

from django.db.models import Prefetch
from django.utils import timezone
from pydantic import BaseModel, ConfigDict

from core.auth.models import OrgUser
from core.calendar.models.event import (
    CalendarEvent,
    CalendarEventReminder,
    CalendarNotification,
)
from core.calendar.reminders import send_due_reminders
from core.seedwork.api_layer import Router

router = Router()


class OutputCalendarEventReminder(BaseModel):
    uuid: UUID
    minutes_before: int
    method: str

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
            Prefetch("reminders", queryset=own_reminders, to_attr="own_reminders"),
        )
    )


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
    send_due_reminders()
    now = timezone.now()
    return CalendarNotification.objects.filter(
        org_user=org_user, event__end_time__gte=now
    ).select_related("event")
