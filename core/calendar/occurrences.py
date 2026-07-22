from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from dateutil.rrule import DAILY, MONTHLY, WEEKLY, YEARLY, rrule
from django.utils import timezone

from core.calendar.models import CalendarEvent, CalendarEventOccurrenceOverride
from core.seedwork.domain_layer import DomainError

# dateutil types rrule's freq parameter is a literal of its frequency
# constants (YEARLY=0 .. DAILY=3)
_RruleFrequency = Literal[0, 1, 2, 3]

_FREQUENCIES: dict[str, _RruleFrequency] = {
    "FREQ=DAILY": DAILY,
    "FREQ=WEEKLY": WEEKLY,
    "FREQ=MONTHLY": MONTHLY,
    "FREQ=YEARLY": YEARLY,
}

# Backstop against scanning an event series without end date forever
MAX_SLOT_SCAN = 500


@dataclass(frozen=True)
class Occurrence:
    event: CalendarEvent
    original_start: datetime
    start_time: datetime
    end_time: datetime
    title: str
    description: str
    location: str
    cancelled: bool


def ensure_aware(dt: datetime) -> datetime:
    # The frontend sends datetimes without timezone, Django wants one
    if timezone.is_naive(dt):
        return timezone.make_aware(dt)
    return dt


def normalize_slot(dt: datetime) -> datetime:
    # dateutil's rrule works at second granularity
    return timezone.localtime(dt).replace(microsecond=0)


def _to_naive_local(dt: datetime) -> datetime:
    return normalize_slot(dt).replace(tzinfo=None)


def _from_naive_local(naive_local: datetime) -> datetime:
    return timezone.make_aware(naive_local)


def _build_rule(event: CalendarEvent) -> rrule:
    frequency = _FREQUENCIES.get(event.recurrence_rule)
    if frequency is None:
        raise DomainError("This recurrence rule is not supported.")
    # to keep a 09 am event at 09 am across daylight savings
    dtstart = _to_naive_local(event.start_time)
    until = None
    if event.recurrence_until is not None:
        until = datetime.combine(event.recurrence_until, dtstart.time())
    return rrule(freq=frequency, dtstart=dtstart, until=until)


def _resolve_occurrence(
    event: CalendarEvent,
    slot: datetime,
    override: CalendarEventOccurrenceOverride | None,
) -> Occurrence:
    duration = event.end_time - event.start_time
    start = slot
    if override is not None and override.start_time is not None:
        start = override.start_time
    end = start + duration
    if override is not None and override.end_time is not None:
        end = override.end_time
    return Occurrence(
        event=event,
        original_start=slot,
        start_time=start,
        end_time=end,
        title=(
            override.title
            if override is not None and override.title is not None
            else event.title
        ),
        description=(
            override.description
            if override is not None and override.description is not None
            else event.description
        ),
        location=(
            override.location
            if override is not None and override.location is not None
            else event.location
        ),
        cancelled=override is not None and override.cancelled,
    )


def _overrides_by_slot(
    event: CalendarEvent,
) -> dict[datetime, CalendarEventOccurrenceOverride]:
    if event.pk is None:  # not saved yet, cannot have overrides
        return {}
    return {
        override.original_start: override
        for override in event.occurrence_overrides.all()
    }


def _series_slots_between(
    event: CalendarEvent, from_dt: datetime, to_dt: datetime
) -> list[datetime]:
    if not event.recurrence_rule:
        slot = event.start_time
        return [slot] if from_dt <= slot <= to_dt else []
    rule = _build_rule(event)
    naive_slots = rule.between(
        _to_naive_local(from_dt), _to_naive_local(to_dt), inc=True
    )
    return [_from_naive_local(naive) for naive in naive_slots[:MAX_SLOT_SCAN]]


def series_contains_slot(event: CalendarEvent, slot: datetime) -> bool:
    if not event.recurrence_rule:
        return normalize_slot(slot) == normalize_slot(event.start_time)
    naive_slot = _to_naive_local(slot)
    rule = _build_rule(event)
    return rule.after(naive_slot, inc=True) == naive_slot


def _happens_between(
    occurrence: Occurrence, from_dt: datetime, to_dt: datetime
) -> bool:
    return occurrence.end_time >= from_dt and occurrence.start_time <= to_dt


def get_occurrences(
    event: CalendarEvent,
    *,
    from_dt: datetime,
    to_dt: datetime,
    include_cancelled: bool = False,
) -> list[Occurrence]:
    slots_in_window = _series_slots_between(event, from_dt, to_dt)
    # an overridden occurrence can happen inside the window even though its actual
    # slot is not in the window (and vice versa)
    all_overrides = _overrides_by_slot(event)
    candidate_slots = set(slots_in_window) | set(all_overrides.keys())

    resolved_occurrences = [
        _resolve_occurrence(event, slot, all_overrides.get(slot))
        for slot in candidate_slots
    ]
    matching_occurrences = [
        occurrence
        for occurrence in resolved_occurrences
        if (include_cancelled or not occurrence.cancelled)
        and _happens_between(occurrence, from_dt, to_dt)
    ]
    return sorted(matching_occurrences, key=lambda occurrence: occurrence.start_time)


def get_occurrence(event: CalendarEvent, slot: datetime) -> Occurrence | None:
    if not series_contains_slot(event, slot):
        return None
    slot = normalize_slot(slot)
    overrides = _overrides_by_slot(event)
    return _resolve_occurrence(event, slot, overrides.get(slot))


def get_next_occurrence(event: CalendarEvent, *, after: datetime) -> Occurrence | None:
    if not event.recurrence_rule:
        if event.start_time <= after:
            return None
        return _resolve_occurrence(event, event.start_time, None)

    overrides = _overrides_by_slot(event)
    candidates = []

    # Overrides may have moved any slot of the series past the after datetime
    for override in overrides.values():
        occurrence = _resolve_occurrence(event, override.original_start, override)
        if not occurrence.cancelled and occurrence.start_time > after:
            candidates.append(occurrence)

    rule = _build_rule(event)
    naive_slot = rule.after(_to_naive_local(after))
    scanned = 0
    while naive_slot is not None and scanned < MAX_SLOT_SCAN:
        slot = _from_naive_local(naive_slot)
        occurrence = _resolve_occurrence(event, slot, overrides.get(slot))
        if not occurrence.cancelled and occurrence.start_time > after:
            candidates.append(occurrence)
            break
        scanned += 1
        naive_slot = rule.after(naive_slot)

    if not candidates:
        return None
    return min(candidates, key=lambda occurrence: occurrence.start_time)
