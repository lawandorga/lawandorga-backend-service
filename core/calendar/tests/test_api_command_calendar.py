from datetime import timedelta

from django.test import Client
from django.utils import timezone

from core.calendar.models import CalendarEvent, CalendarEventReminder
from core.tests.test_helpers import create_raw_org, create_raw_org_user


def test_create_event_with_reminders_via_command_endpoint(db):
    org = create_raw_org(save=True)
    user = create_raw_org_user(org=org, email="user@test.de", save=True)

    client = Client()
    client.login(**getattr(user, "login_data"))

    start = timezone.localtime(timezone.now() + timedelta(days=2))
    end = start + timedelta(hours=1)

    response = client.post(
        "/api/command/",
        {
            "action": "calendar/create_event",
            "title": "With reminder",
            "event_type": "MEETING",
            "start_time": start.strftime("%Y-%m-%dT%H:%M"),
            "end_time": end.strftime("%Y-%m-%dT%H:%M"),
            "recurrence_rule": "",
            "recurrence_until": "||NULL||",
            "grant_targets": "||EMPTYARRAY||",
            "reminders": "||ARRAY||EMAIL:60||ARRAYSEPERATOR||IN_APP:30",
        },
    )

    assert response.status_code == 200
    event = CalendarEvent.objects.get(title="With reminder")
    created = set(event.reminders.values_list("method", "minutes_before"))
    assert created == {
        (CalendarEventReminder.Method.EMAIL, 60),
        (CalendarEventReminder.Method.IN_APP, 30),
    }
