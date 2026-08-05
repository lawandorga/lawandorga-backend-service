from datetime import timedelta

from django.test import Client
from django.utils import timezone

from core.calendar.models import (
    CalendarEvent,
    CalendarEventReminder,
    CalendarEventShare,
    CalendarNotification,
)
from core.tests.test_helpers import (
    create_raw_group,
    create_raw_org,
    create_raw_org_user,
)


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
    event_invited.grant_access(
        by=creator,
        shared_user=guest,
        access_level=CalendarEventShare.AccessLevel.VIEW,
    )

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

    response = client.get("/api/calendar/query/events/")
    assert response.status_code == 200
    data = response.json()

    titles = {item["title"] for item in data}
    assert "Invited" in titles
    assert "Guest owns" in titles
    assert "Creator only" not in titles


def test_query_calendar_events_returns_group_shared_events(db):
    org = create_raw_org(save=True)
    creator = create_raw_org_user(org=org, email="creator@test.de", save=True)
    group_member = create_raw_org_user(
        org=org, email="group-member@test.de", name="Group Member", save=True
    )
    unrelated = create_raw_org_user(
        org=org, email="unrelated@test.de", name="Unrelated", save=True
    )
    group = create_raw_group(org=org, members=[group_member], save=True)

    start = timezone.now()
    event_group_shared = CalendarEvent.create(
        creator=creator,
        title="Group shared",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=start + timedelta(hours=1),
    )
    event_group_shared.save()
    event_group_shared.grant_access(
        by=creator,
        shared_group=group,
        access_level=CalendarEventShare.AccessLevel.VIEW,
    )

    member_client = Client()
    member_client.login(**getattr(group_member, "login_data"))
    member_response = member_client.get("/api/calendar/query/events/")
    assert member_response.status_code == 200
    member_titles = {item["title"] for item in member_response.json()}
    assert "Group shared" in member_titles

    unrelated_client = Client()
    unrelated_client.login(**getattr(unrelated, "login_data"))
    unrelated_response = unrelated_client.get("/api/calendar/query/events/")
    assert unrelated_response.status_code == 200
    unrelated_titles = {item["title"] for item in unrelated_response.json()}
    assert "Group shared" not in unrelated_titles


def test_query_calendar_events_returns_org_shared_events(db):
    org = create_raw_org(save=True)
    creator = create_raw_org_user(org=org, email="creator@test.de", save=True)
    org_member = create_raw_org_user(
        org=org, email="org-member@test.de", name="Org Member", save=True
    )

    start = timezone.now()
    event_org_shared = CalendarEvent.create(
        creator=creator,
        title="Org shared",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=start + timedelta(hours=1),
    )
    event_org_shared.save()
    event_org_shared.grant_access(
        by=creator,
        shared_org=org,
        access_level=CalendarEventShare.AccessLevel.VIEW,
    )

    client = Client()
    client.login(**getattr(org_member, "login_data"))

    response = client.get("/api/calendar/query/events/")
    assert response.status_code == 200
    titles = {item["title"] for item in response.json()}
    assert "Org shared" in titles


def test_query_notifications_returns_only_own(db):
    org = create_raw_org(save=True)
    user = create_raw_org_user(org=org, email="user@test.de", save=True)
    other = create_raw_org_user(org=org, email="other@test.de", name="Other", save=True)

    start = timezone.now()
    event = CalendarEvent.create(
        creator=user,
        title="Court date",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=start + timedelta(hours=1),
    )
    event.save()
    CalendarNotification.objects.create(org_user=user, event=event, message="Yours")
    CalendarNotification.objects.create(org_user=other, event=event, message="Theirs")

    client = Client()
    client.login(**getattr(user, "login_data"))

    response = client.get("/api/calendar/query/notifications/")
    assert response.status_code == 200
    messages = {item["message"] for item in response.json()}
    assert messages == {"Yours"}


def test_query_notifications_dispatches_due_in_app_reminders(db):
    org = create_raw_org(save=True)
    user = create_raw_org_user(org=org, email="user@test.de", save=True)

    start = timezone.now() + timedelta(hours=2)
    event = CalendarEvent.create(
        creator=user,
        title="Court date",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=start + timedelta(hours=1),
    )
    event.save()

    reminder = CalendarEventReminder.create(
        event=event,
        org_user=user,
        minutes_before=60,
        method=CalendarEventReminder.Method.IN_APP,
    )
    reminder.save()
    reminder.remind_at = timezone.now() - timedelta(minutes=1)
    reminder.dispatched_at = None
    reminder.save(update_fields=["remind_at", "dispatched_at"])

    client = Client()
    client.login(**getattr(user, "login_data"))

    response = client.get("/api/calendar/query/notifications/")
    assert response.status_code == 200
    messages = {item["message"] for item in response.json()}
    expected_message = (
        f'"{event.title}" starts in 1 hour at '
        f'{timezone.localtime(event.start_time).strftime("%Y-%m-%d %H:%M %Z")}.'
    )
    assert messages == {expected_message}

    reminder.refresh_from_db()
    assert reminder.dispatched_at is not None


def test_query_notifications_excludes_ended_events(db):
    org = create_raw_org(save=True)
    user = create_raw_org_user(org=org, email="user@test.de", save=True)

    now = timezone.now()
    past_event = CalendarEvent.create(
        creator=user,
        title="Past",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=now - timedelta(hours=3),
        end_time=now - timedelta(hours=2),
    )
    past_event.save()
    upcoming_event = CalendarEvent.create(
        creator=user,
        title="Upcoming",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=now + timedelta(hours=1),
        end_time=now + timedelta(hours=2),
    )
    upcoming_event.save()
    CalendarNotification.objects.create(org_user=user, event=past_event, message="Over")
    CalendarNotification.objects.create(
        org_user=user, event=upcoming_event, message="Upcoming"
    )

    client = Client()
    client.login(**getattr(user, "login_data"))

    response = client.get("/api/calendar/query/notifications/")
    assert response.status_code == 200
    messages = {item["message"] for item in response.json()}
    assert messages == {"Upcoming"}
