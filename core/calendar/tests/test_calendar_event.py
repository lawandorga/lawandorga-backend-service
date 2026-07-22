from datetime import timedelta

import pytest
from django.utils import timezone

from core.calendar.models import CalendarEvent, CalendarEventShare, RecurrenceRule
from core.seedwork.domain_layer import DomainError
from core.tests import test_helpers


def test_recurrence_rule_normalizes_and_validates():
    rule = RecurrenceRule("  FREQ=DAILY  ")

    assert rule == "FREQ=DAILY"
    assert isinstance(rule, str)


def test_recurrence_rule_rejects_unsupported_rules():
    with pytest.raises(DomainError):
        RecurrenceRule("FREQ=DAILY;INTERVAL=2")
    with pytest.raises(DomainError):
        RecurrenceRule("FREQ=HOURLY")


def test_create_calendar_event_with_recurrence_rule(db):
    user_data = test_helpers.create_org_user(save=True)
    user = user_data["org_user"]
    start = timezone.now()
    end = start + timedelta(hours=1)
    until_date = (start + timedelta(days=7)).date()

    event = CalendarEvent.create(
        creator=user,
        title="Daily standup",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=end,
        recurrence_rule=RecurrenceRule("FREQ=DAILY"),
        recurrence_until=until_date,
    )
    event.save()

    assert event.recurrence_rule == "FREQ=DAILY"
    assert event.recurrence_until == until_date


def test_update_calendar_event_recurrence_rule(db):
    user_data = test_helpers.create_org_user(save=True)
    user = user_data["org_user"]
    start = timezone.now()
    end = start + timedelta(hours=1)

    event = CalendarEvent.create(
        creator=user,
        title="Weekly meeting",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=end,
        recurrence_rule=RecurrenceRule("FREQ=WEEKLY"),
    )
    event.save()

    event.update_information(recurrence_rule=RecurrenceRule("FREQ=MONTHLY"))
    event.save()

    assert event.recurrence_rule == "FREQ=MONTHLY"


def test_update_information_keeps_end_time_when_argument_is_omitted(db):
    user_data = test_helpers.create_org_user(save=True)
    user = user_data["org_user"]
    start = timezone.now()
    end = start + timedelta(hours=1)

    event = CalendarEvent.create(
        creator=user,
        title="Weekly meeting",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=end,
    )
    event.save()

    event.update_information(title="Renamed meeting")

    assert event.title == "Renamed meeting"
    assert event.end_time == end


def test_update_information_keeps_end_time_when_none_is_passed(db):
    user_data = test_helpers.create_org_user(save=True)
    user = user_data["org_user"]
    start = timezone.now()
    end = start + timedelta(hours=1)

    event = CalendarEvent.create(
        creator=user,
        title="Weekly meeting",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=end,
    )
    event.save()

    event.update_information(end_time=None)

    assert event.end_time == end


def test_save_creates_protected_creator_acl_share(db):
    creator_data = test_helpers.create_org_user(save=True)
    creator = creator_data["org_user"]
    event = CalendarEvent.create(
        creator=creator,
        title="Ownership",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=timezone.now(),
        end_time=timezone.now() + timedelta(hours=1),
    )

    event.save()

    creator_share = event.shares.get(shared_user=creator)
    assert creator_share.access_level == CalendarEventShare.AccessLevel.ADMIN

    with pytest.raises(DomainError):
        creator_share.delete()


def test_access_levels_allow_view_but_not_edit_for_view_shares(db):
    creator_data = test_helpers.create_org_user(save=True)
    viewer_data = test_helpers.create_org_user(
        org=creator_data["org_user"].org,
        email="viewer@test.de",
        name="Viewer",
        save=True,
    )
    editor_data = test_helpers.create_org_user(
        org=creator_data["org_user"].org,
        email="editor@test.de",
        name="Editor",
        save=True,
    )

    creator = creator_data["org_user"]
    viewer = viewer_data["org_user"]
    editor = editor_data["org_user"]

    event = CalendarEvent.create(
        creator=creator,
        title="ACL",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=timezone.now(),
        end_time=timezone.now() + timedelta(hours=1),
    )
    event.save()

    event.grant_access(
        by=creator,
        shared_user=viewer,
        access_level=CalendarEventShare.AccessLevel.VIEW,
    )
    event.grant_access(
        by=creator,
        shared_user=editor,
        access_level=CalendarEventShare.AccessLevel.EDIT,
    )

    assert event.has_view_access(viewer) is True
    assert event.has_edit_access(viewer) is False
    assert event.has_view_access(editor) is True
    assert event.has_edit_access(editor) is True
