from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from core.events.models import CalendarEvent, RecurrenceRule
from core.tests import test_helpers


class TestCalendarEvent(TestCase):
    def test_recurrence_rule_normalizes_and_validates(self):
        rule = RecurrenceRule("  FREQ=DAILY;INTERVAL=1  ")

        assert rule == "FREQ=DAILY;INTERVAL=1"
        assert isinstance(rule, str)

    def test_create_calendar_event_with_recurrence_rule(self):
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
            recurrence_rule=RecurrenceRule("FREQ=DAILY;INTERVAL=1"),
            recurrence_until=until_date,
        )
        event.save()

        assert event.recurrence_rule == "FREQ=DAILY;INTERVAL=1"
        assert event.recurrence_until == until_date

    def test_update_calendar_event_recurrence_rule(self):
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
