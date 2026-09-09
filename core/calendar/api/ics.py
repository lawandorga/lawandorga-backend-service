import uuid
from datetime import timedelta

import ics
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from core.calendar.models import CalendarEvent, CalendarLink
from core.calendar.occurrences import get_occurrences


def api_get_ics_calendar_link(request, calendar_uuid: uuid.UUID):
    calendar_link = get_object_or_404(CalendarLink, uuid=calendar_uuid)
    events = (
        CalendarEvent.get_accessible_events_for_user(calendar_link.org_user)
        .filter(event_type__in=calendar_link.event_types)
        .prefetch_related("occurrence_overrides")
    )
    now = timezone.now()
    calendar = ics.Calendar()
    for event in events:
        for occurrence in get_occurrences(
            event,
            from_dt=now - timedelta(days=1),
            to_dt=now + timedelta(days=365 * 5),
        ):
            ics_event = ics.Event()
            ics_event.name = occurrence.title
            ics_event.begin = occurrence.start_time
            ics_event.end = occurrence.end_time
            ics_event.description = occurrence.description
            ics_event.location = occurrence.location
            calendar.events.add(ics_event)
    return HttpResponse(calendar.serialize(), content_type="text/calendar")
