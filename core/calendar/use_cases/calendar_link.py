from django.conf import settings

from core.auth.models import OrgUser
from core.calendar.models import CalendarLink
from core.seedwork.use_case_layer import use_case


@use_case
def create_calendar_link(
    __actor: OrgUser,
    event_types: list[str],
) -> dict:
    calendar_link = CalendarLink.create(__actor, event_types)
    calendar_link.save()
    return {
        "uuid": str(calendar_link.uuid),
        "event_types": calendar_link.event_types,
        "calendar_url": f"{settings.CALENDAR_LINK_URL}{calendar_link.uuid}.ics",
    }
