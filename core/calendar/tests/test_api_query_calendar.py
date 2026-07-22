from datetime import timedelta

from django.test import Client
from django.utils import timezone

from core.calendar.models import (
    CalendarEvent,
    CalendarEventOccurrenceOverride,
    CalendarEventShare,
    CalendarNotification,
    RecurrenceRule,
)
from core.tests.test_helpers import (
    create_raw_group,
    create_raw_org,
    create_raw_org_user,
)


def test_query_calendar_occurrences_expands_series_and_applies_overrides(db):
    org = create_raw_org(save=True)
    creator = create_raw_org_user(org=org, email="creator@test.de", save=True)

    start = timezone.now().replace(microsecond=0)
    event = CalendarEvent.create(
        creator=creator,
        title="Standup",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=start + timedelta(hours=1),
        recurrence_rule=RecurrenceRule("FREQ=WEEKLY"),
    )
    event.save()

    # cancel the second occurrence, move the third two hours later
    CalendarEventOccurrenceOverride.objects.create(
        event=event, original_start=start + timedelta(weeks=1), cancelled=True
    )
    CalendarEventOccurrenceOverride.objects.create(
        event=event,
        original_start=start + timedelta(weeks=2),
        start_time=start + timedelta(weeks=2, hours=2),
        title="Standup (moved)",
    )

    client = Client()
    client.login(**getattr(creator, "login_data"))

    response = client.get(
        "/api/calendar/query/occurrences/",
        {
            "from_dt": (start - timedelta(minutes=1)).isoformat(),
            "to_dt": (start + timedelta(weeks=2, hours=3)).isoformat(),
        },
    )
    assert response.status_code == 200
    occurrences = response.json()

    # the first slot plus the moved third slot; the cancelled second is excluded
    assert len(occurrences) == 2
    titles = {item["title"] for item in occurrences}
    assert titles == {"Standup", "Standup (moved)"}
    assert all(item["event_uuid"] == str(event.uuid) for item in occurrences)


def test_query_calendar_occurrences_hides_inaccessible_events(db):
    org = create_raw_org(save=True)
    creator = create_raw_org_user(org=org, email="creator@test.de", save=True)
    outsider = create_raw_org_user(org=org, email="outsider@test.de", save=True)

    start = timezone.now().replace(microsecond=0)
    event = CalendarEvent.create(
        creator=creator,
        title="Private",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=start + timedelta(hours=1),
    )
    event.save()

    client = Client()
    client.login(**getattr(outsider, "login_data"))

    response = client.get(
        "/api/calendar/query/occurrences/",
        {
            "from_dt": (start - timedelta(days=1)).isoformat(),
            "to_dt": (start + timedelta(days=1)).isoformat(),
        },
    )
    assert response.status_code == 200
    assert response.json() == []


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
    CalendarNotification.objects.create(
        org_user=user, event=event, message="Yours", occurrence_end=event.end_time
    )
    CalendarNotification.objects.create(
        org_user=other, event=event, message="Theirs", occurrence_end=event.end_time
    )

    client = Client()
    client.login(**getattr(user, "login_data"))

    response = client.get("/api/calendar/query/notifications/")
    assert response.status_code == 200
    messages = {item["message"] for item in response.json()}
    assert messages == {"Yours"}


def test_query_notifications_excludes_ended_occurrences(db):
    org = create_raw_org(save=True)
    user = create_raw_org_user(org=org, email="user@test.de", save=True)

    now = timezone.now()
    event = CalendarEvent.create(
        creator=user,
        title="Standup",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=now - timedelta(hours=3),
        end_time=now - timedelta(hours=2),
    )
    event.save()
    CalendarNotification.objects.create(
        org_user=user,
        event=event,
        message="Over",
        occurrence_end=now - timedelta(hours=2),
    )
    CalendarNotification.objects.create(
        org_user=user,
        event=event,
        message="Upcoming",
        occurrence_end=now + timedelta(hours=2),
    )

    client = Client()
    client.login(**getattr(user, "login_data"))

    response = client.get("/api/calendar/query/notifications/")
    assert response.status_code == 200
    messages = {item["message"] for item in response.json()}
    assert messages == {"Upcoming"}


def test_query_calendar_events_includes_occurrence_overrides(db):
    org = create_raw_org(save=True)
    user = create_raw_org_user(org=org, email="user@test.de", save=True)

    start = timezone.now() + timedelta(days=1)
    event = CalendarEvent.create(
        creator=user,
        title="Standup",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=start + timedelta(hours=1),
        recurrence_rule=RecurrenceRule("FREQ=WEEKLY"),
    )
    event.save()
    slot = start + timedelta(days=7)
    CalendarEventOccurrenceOverride.objects.create(
        event=event, original_start=slot, cancelled=True
    )

    client = Client()
    client.login(**getattr(user, "login_data"))

    response = client.get("/api/calendar/query/events/")
    assert response.status_code == 200
    payload = next(item for item in response.json() if item["title"] == "Standup")
    assert len(payload["overrides"]) == 1
    assert payload["overrides"][0]["cancelled"] is True
