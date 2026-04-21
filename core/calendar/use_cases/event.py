from datetime import date, datetime

from core.auth.models.org_user import OrgUser
from core.calendar.models import CalendarEvent, RecurrenceRule
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
