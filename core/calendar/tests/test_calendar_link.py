from datetime import timedelta

from django.test import Client
from django.utils import timezone

from core.calendar.models import CalendarEvent, CalendarLink
from core.tests.test_helpers import create_raw_org, create_raw_org_user


def test_calendar_link_command_creates_filtered_public_ics_calendar(db):
    org = create_raw_org(save=True)
    user = create_raw_org_user(org=org, email="user@test.de", save=True)
    start = timezone.now() + timedelta(days=1)
    meeting = CalendarEvent.create(
        creator=user,
        title="Included meeting",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=start + timedelta(hours=1),
    )
    meeting.save()
    task = CalendarEvent.create(
        creator=user,
        title="Excluded task",
        event_type=CalendarEvent.EventType.TASK,
        start_time=start,
        end_time=start + timedelta(hours=1),
    )
    task.save()

    client = Client()
    client.login(**getattr(user, "login_data"))
    response = client.post(
        "/api/command/",
        {"action": "calendar/create_calendar_link", "event_types": "||ARRAY||MEETING"},
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["event_types"] == ["MEETING"]
    calendar_link = CalendarLink.objects.get(org_user=user)
    assert response_data["calendar_url"].endswith(f"{calendar_link.uuid}.ics")
    response = Client().get(f"/api/calendar/ics/{calendar_link.uuid}.ics")

    assert response.status_code == 200
    assert response["Content-Type"] == "text/calendar"
    assert "Included meeting" in response.content.decode()
    assert "Excluded task" not in response.content.decode()

    repeated_response = Client().get(f"/api/calendar/ics/{calendar_link.uuid}.ics")
    first_calendar = response.content.decode()
    second_calendar = repeated_response.content.decode()
    assert "DTSTAMP:" in first_calendar
    assert f"UID:{meeting.uuid}-" in first_calendar
    assert {
        line for line in first_calendar.splitlines() if line.startswith("UID:")
    } == {line for line in second_calendar.splitlines() if line.startswith("UID:")}
