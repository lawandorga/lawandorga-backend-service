from datetime import date, datetime, timedelta
from datetime import timezone as dt_timezone

import pytest
from django.utils import timezone

from core.calendar.models import (
    CalendarEvent,
    CalendarEventOccurrenceOverride,
    RecurrenceRule,
)
from core.calendar.occurrences import (
    get_next_occurrence,
    get_occurrences,
    series_contains_slot,
)
from core.seedwork.domain_layer import DomainError
from core.tests import test_helpers

BERLIN_WINTER = dt_timezone(timedelta(hours=1))  # CET
BERLIN_SUMMER = dt_timezone(timedelta(hours=2))  # CEST


def _create_event(actor, *, start, duration=timedelta(hours=1), rule="", until=None):
    event = CalendarEvent.create(
        creator=actor,
        title="Standup",
        event_type=CalendarEvent.EventType.MEETING,
        start_time=start,
        end_time=start + duration,
        recurrence_rule=RecurrenceRule.create(rule or None),
        recurrence_until=until,
    )
    event.save()
    return event


def _actor():
    return test_helpers.create_org_user(save=True)["org_user"]


def test_non_recurring_event_has_single_occurrence(db):
    actor = _actor()
    start = timezone.now() + timedelta(days=1)
    event = _create_event(actor, start=start)

    inside = get_occurrences(
        event, from_dt=start - timedelta(days=1), to_dt=start + timedelta(days=1)
    )
    outside = get_occurrences(
        event, from_dt=start + timedelta(days=2), to_dt=start + timedelta(days=3)
    )

    assert len(inside) == 1
    assert inside[0].start_time == start
    assert inside[0].end_time == start + timedelta(hours=1)
    assert outside == []


def test_weekly_series_expands_within_window(db):
    actor = _actor()
    start = datetime(2026, 1, 7, 9, 0, tzinfo=BERLIN_WINTER)  # a Wednesday
    event = _create_event(actor, start=start, rule="FREQ=WEEKLY")

    occurrences = get_occurrences(
        event,
        from_dt=start,
        to_dt=start + timedelta(days=28),
    )

    assert len(occurrences) == 5  # inclusive: weeks 0..4
    assert occurrences[1].start_time == start + timedelta(days=7)
    assert occurrences[0].title == "Standup"


def test_weekly_series_keeps_wall_clock_time_across_dst(db):
    actor = _actor()
    # 09:00 Berlin in winter (CET, UTC+1); DST starts 2026-03-29.
    start = datetime(2026, 1, 7, 9, 0, tzinfo=BERLIN_WINTER)
    event = _create_event(actor, start=start, rule="FREQ=WEEKLY")

    occurrences = get_occurrences(
        event,
        from_dt=datetime(2026, 4, 1, tzinfo=BERLIN_SUMMER),
        to_dt=datetime(2026, 4, 15, tzinfo=BERLIN_SUMMER),
    )

    assert len(occurrences) == 2
    for occurrence in occurrences:
        local = timezone.localtime(occurrence.start_time)
        assert (local.hour, local.minute) == (9, 0)


def test_until_includes_the_last_day(db):
    actor = _actor()
    start = datetime(2026, 1, 5, 9, 0, tzinfo=BERLIN_WINTER)
    event = _create_event(actor, start=start, rule="FREQ=DAILY", until=date(2026, 1, 8))

    occurrences = get_occurrences(
        event, from_dt=start, to_dt=start + timedelta(days=30)
    )

    assert len(occurrences) == 4  # 5th, 6th, 7th, 8th
    last_local = timezone.localtime(occurrences[-1].start_time)
    assert last_local.date() == date(2026, 1, 8)


def test_cancelled_occurrence_is_skipped(db):
    actor = _actor()
    start = datetime(2026, 1, 5, 9, 0, tzinfo=BERLIN_WINTER)
    event = _create_event(actor, start=start, rule="FREQ=DAILY")
    CalendarEventOccurrenceOverride.objects.create(
        event=event, original_start=start + timedelta(days=1), cancelled=True
    )

    occurrences = get_occurrences(
        event, from_dt=start, to_dt=start + timedelta(days=2, hours=12)
    )

    starts = [occurrence.start_time for occurrence in occurrences]
    assert starts == [start, start + timedelta(days=2)]

    with_cancelled = get_occurrences(
        event,
        from_dt=start,
        to_dt=start + timedelta(days=2, hours=12),
        include_cancelled=True,
    )
    assert len(with_cancelled) == 3


def test_moved_occurrence_uses_override_times_and_fields(db):
    actor = _actor()
    start = datetime(2026, 1, 5, 9, 0, tzinfo=BERLIN_WINTER)
    event = _create_event(actor, start=start, rule="FREQ=WEEKLY")
    slot = start + timedelta(days=7)
    moved_start = slot + timedelta(hours=3)
    CalendarEventOccurrenceOverride.objects.create(
        event=event,
        original_start=slot,
        start_time=moved_start,
        title="Standup (moved)",
        location="Room 2",
    )

    occurrences = get_occurrences(
        event, from_dt=start, to_dt=start + timedelta(days=10)
    )

    moved = next(o for o in occurrences if o.original_start == slot)
    assert moved.start_time == moved_start
    assert moved.end_time == moved_start + timedelta(hours=1)  # duration kept
    assert moved.title == "Standup (moved)"
    assert moved.location == "Room 2"
    assert moved.description == ""  # inherited


def test_occurrence_moved_into_window_is_found(db):
    actor = _actor()
    start = datetime(2026, 1, 5, 9, 0, tzinfo=BERLIN_WINTER)
    event = _create_event(actor, start=start, rule="FREQ=WEEKLY")
    slot = start + timedelta(days=28)  # outside the window
    moved_start = start + timedelta(days=9)  # inside it
    CalendarEventOccurrenceOverride.objects.create(
        event=event, original_start=slot, start_time=moved_start
    )

    occurrences = get_occurrences(
        event, from_dt=start + timedelta(days=8), to_dt=start + timedelta(days=10)
    )

    assert [o.start_time for o in occurrences] == [moved_start]


def test_next_occurrence_skips_cancelled_slots(db):
    actor = _actor()
    start = datetime(2026, 1, 5, 9, 0, tzinfo=BERLIN_WINTER)
    event = _create_event(actor, start=start, rule="FREQ=DAILY")
    CalendarEventOccurrenceOverride.objects.create(
        event=event, original_start=start + timedelta(days=1), cancelled=True
    )

    following = get_next_occurrence(event, after=start)

    assert following is not None
    assert following.start_time == start + timedelta(days=2)


def test_next_occurrence_is_none_after_series_end(db):
    actor = _actor()
    start = datetime(2026, 1, 5, 9, 0, tzinfo=BERLIN_WINTER)
    event = _create_event(actor, start=start, rule="FREQ=DAILY", until=date(2026, 1, 7))

    assert get_next_occurrence(event, after=start + timedelta(days=30)) is None


def test_next_occurrence_for_non_recurring_event(db):
    actor = _actor()
    start = timezone.now() + timedelta(days=1)
    event = _create_event(actor, start=start)

    next_occurrence = get_next_occurrence(event, after=timezone.now())
    assert next_occurrence is not None
    assert next_occurrence.start_time == start
    assert get_next_occurrence(event, after=start) is None


def test_series_contains_slot(db):
    actor = _actor()
    start = datetime(2026, 1, 5, 9, 0, tzinfo=BERLIN_WINTER)
    event = _create_event(actor, start=start, rule="FREQ=WEEKLY")

    assert series_contains_slot(event, start + timedelta(days=7))
    assert not series_contains_slot(event, start + timedelta(days=3))


def test_unsupported_stored_rule_raises(db):
    actor = _actor()
    start = timezone.now()
    event = _create_event(actor, start=start)
    # recurrence_rule is a plain CharField, so an unsupported value can be saved
    # without going through RecurrenceRule (e.g. the admin, a data migration)
    event.recurrence_rule = "FREQ=HOURLY"
    event.save()

    with pytest.raises(DomainError):
        get_occurrences(event, from_dt=start, to_dt=start + timedelta(days=1))
