from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from core.auth.models import OrgUser
from core.calendar.models.event import CalendarEvent
from core.seedwork.api_layer import Router

router = Router()


class OutputCalendarEvent(BaseModel):
    uuid: UUID
    creator_id: int
    creator_name: str
    title: str
    description: str
    event_type: str
    start_time: datetime
    end_time: datetime | None
    location: str
    recurrence_rule: str
    recurrence_until: date | None
    guest_user_ids: list[int]
    guest_user_names: list[str]
    created: datetime
    updated: datetime

    model_config = ConfigDict(from_attributes=True)


@router.get(
    url="events/",
    output_schema=list[OutputCalendarEvent],
)
def query__calendar_events(org_user: OrgUser):
    return (
        CalendarEvent.get_accessible_events_for_user(org_user)
        .select_related("creator", "creator__user")
        .prefetch_related("guest_users", "guests")
    )
