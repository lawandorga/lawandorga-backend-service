from datetime import timedelta

import pytest
from django.utils import timezone

from core.calendar.models import CalendarEvent, CalendarNotification
from core.calendar.use_cases.notification import (
    mark_all_notifications_read,
    mark_notification_read,
)
from core.seedwork.domain_layer import DomainError
from core.tests import test_helpers


def _create_event(actor):
    start = timezone.now() + timedelta(hours=2)
    event = CalendarEvent.create(
        creator=actor,
        title="Court date",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=start + timedelta(hours=1),
    )
    event.save()
    return event


def _create_notification(org_user, event):
    return CalendarNotification.objects.create(
        org_user=org_user,
        event=event,
        message="A reminder",
        occurrence_end=event.end_time,
    )


def test_mark_notification_read_sets_read_at(db):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    event = _create_event(actor)
    notification = _create_notification(actor, event)

    mark_notification_read(__actor=actor, notification_uuid=notification.uuid)

    notification.refresh_from_db()
    assert notification.read_at is not None


def test_mark_notification_read_rejects_other_users(db):
    org = test_helpers.create_org("Shared Org", save=True)["org"]
    owner = test_helpers.create_org_user(email="owner@law-orga.de", org=org, save=True)[
        "org_user"
    ]
    other = test_helpers.create_org_user(email="other@law-orga.de", org=org, save=True)[
        "org_user"
    ]
    event = _create_event(owner)
    notification = _create_notification(owner, event)

    with pytest.raises(DomainError):
        mark_notification_read(__actor=other, notification_uuid=notification.uuid)

    notification.refresh_from_db()
    assert notification.read_at is None


def test_mark_all_notifications_read(db):
    actor = test_helpers.create_org_user(save=True)["org_user"]
    event = _create_event(actor)
    _create_notification(actor, event)
    _create_notification(actor, event)

    mark_all_notifications_read(__actor=actor)

    unread = CalendarNotification.objects.filter(org_user=actor, read_at__isnull=True)
    assert unread.count() == 0
