from datetime import timedelta

from django.test import Client
from django.utils import timezone

from core.calendar.models import CalendarEvent
from core.tests.test_helpers import create_raw_org, create_raw_org_user


def test_query_calendar_events_returns_accessible_events(db):
    org = create_raw_org(save=True)
    creator = create_raw_org_user(org=org, email="creator@test.de", save=True)
    guest = create_raw_org_user(org=org, email="guest@test.de", name="Guest", save=True)

    start = timezone.now()

    # Event creator owns (not visible to guest)
    event_creator_only = CalendarEvent.create(
        creator=creator,
        title="Creator only",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=start + timedelta(hours=1),
    )
    event_creator_only.save()

    # Event creator invites guest (visible to guest)
    event_invited = CalendarEvent.create(
        creator=creator,
        title="Invited",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start + timedelta(days=1),
        end_time=start + timedelta(days=1, hours=1),
    )
    event_invited.save()
    event_invited.guest_users.add(guest)

    # Event guest owns (visible to guest)
    event_guest_owns = CalendarEvent.create(
        creator=guest,
        title="Guest owns",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start + timedelta(days=2),
        end_time=start + timedelta(days=2, hours=1),
    )
    event_guest_owns.save()

    client = Client()
    client.login(**getattr(guest, "login_data"))

    response = client.get("/api/calendar/query/")
    assert response.status_code == 200
    data = response.json()

    titles = {item["title"] for item in data}
    assert "Invited" in titles
    assert "Guest owns" in titles
    assert "Creator only" not in titles
