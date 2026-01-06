import ics
from django.db.models import Q

from core.auth.models.org_user import OrgUser
from core.events.models import EventsEvent


def get_ics_calendar(org_user: OrgUser):

    events = EventsEvent.objects.filter(
        Q(level="META", org__meta=org_user.org.meta)
        | Q(level="GLOBAL")
        | Q(org=org_user.org)
    )

    c = ics.Calendar()
    for event in events:
        ics_event = ics.Event()
        ics_event.name = event.name
        ics_event.begin = event.start_time
        ics_event.end = event.end_time
        ics_event.description = event.description
        ics_event.organizer = event.org.name
        c.events.add(ics_event)
    return c.serialize()
