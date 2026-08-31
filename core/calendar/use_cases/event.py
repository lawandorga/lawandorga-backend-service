from datetime import date, datetime
from uuid import UUID

from django.db import transaction

from core.auth.models.org_user import OrgUser
from core.calendar.models import CalendarEvent, CalendarEventShare, RecurrenceRule
from core.calendar.occurrences import ensure_aware
from core.calendar.reminders import resync_event_reminders
from core.calendar.use_cases.reminder import parse_reminder, save_new_reminder
from core.org.models import Group
from core.seedwork.domain_layer import DomainError
from core.seedwork.use_case_layer import use_case
from core.seedwork.use_case_layer.error import UseCaseError


def _parse_grant_target(target: str) -> tuple[str, int]:
    raw_type, raw_id = target.split(":", 1)
    if raw_type not in {"user", "group", "org"}:
        raise UseCaseError("Invalid grant target type.")

    try:
        target_id = int(raw_id)
    except ValueError as exc:
        raise UseCaseError("Visible to is malformed.") from exc

    return raw_type, target_id


def _apply_grants(
    event: CalendarEvent,
    *,
    actor: OrgUser,
    targets: list[str],
    access_level: CalendarEventShare.AccessLevel,
) -> None:
    for target in targets:
        target_type, target_id = _parse_grant_target(target)
        if target_type == "user":
            event.grant_access(
                by=actor,
                access_level=access_level,
                shared_user=OrgUser.objects.get(pk=target_id),
            )
        elif target_type == "group":
            event.grant_access(
                by=actor,
                access_level=access_level,
                shared_group=Group.objects.get(pk=target_id),
            )
        else:
            # the only org an actor can share with is their own
            event.grant_access(
                by=actor,
                access_level=access_level,
                shared_org=actor.org,
            )


def _grant_access(
    event: CalendarEvent,
    *,
    actor: OrgUser,
    view_grant_targets: list[str] | None,
    edit_grant_targets: list[str] | None,
) -> None:
    if view_grant_targets is None and edit_grant_targets is None:
        return

    # edit is granted last so it wins for a target named in both lists
    grants = [
        (CalendarEventShare.AccessLevel.VIEW, view_grant_targets or []),
        (CalendarEventShare.AccessLevel.EDIT, edit_grant_targets or []),
    ]

    with transaction.atomic():
        event.shares.exclude(shared_user=event.creator).delete()
        for access_level, targets in grants:
            _apply_grants(
                event, actor=actor, targets=targets, access_level=access_level
            )


@use_case
def create_event(
    __actor: OrgUser,
    title: str,
    event_type: CalendarEvent.EventType,
    start_time: datetime,
    end_time: datetime | None = None,
    description: str | None = None,
    location: str | None = None,
    recurrence_rule: str | None = None,
    recurrence_until: date | None = None,
    is_all_day: bool = False,
    view_grant_targets: list[str] | None = None,
    edit_grant_targets: list[str] | None = None,
    reminders: list[str] | None = None,
) -> CalendarEvent:
    start_time = ensure_aware(start_time)
    end_time = ensure_aware(end_time) if end_time is not None else None
    parsed_reminders = {parse_reminder(raw) for raw in reminders or []}

    event = CalendarEvent.create(
        creator=__actor,
        title=title,
        event_type=event_type,
        start_time=start_time,
        end_time=end_time or start_time,
        description=description or "",
        location=location or "",
        recurrence_rule=RecurrenceRule.create(recurrence_rule),
        recurrence_until=recurrence_until,
        is_all_day=is_all_day,
    )

    # a reminder that cannot be scheduled aborts the whole creation, so the
    # event must not survive on its own
    with transaction.atomic():
        event.save()
        _grant_access(
            event,
            actor=__actor,
            view_grant_targets=view_grant_targets,
            edit_grant_targets=edit_grant_targets,
        )
        for method, minutes_before in parsed_reminders:
            save_new_reminder(
                event=event,
                org_user=__actor,
                minutes_before=minutes_before,
                method=method,
            )
    return event


@use_case
def update_event(
    __actor: OrgUser,
    event_uuid: UUID,
    title: str | None = None,
    description: str | None = None,
    event_type: CalendarEvent.EventType | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    location: str | None = None,
    recurrence_rule: str | None = None,
    recurrence_until: date | None = None,
    is_all_day: bool | None = None,
    view_grant_targets: list[str] | None = None,
    edit_grant_targets: list[str] | None = None,
) -> CalendarEvent:
    event = CalendarEvent.objects.get(uuid=event_uuid)

    if not event.has_edit_access(__actor):
        raise DomainError("You can only edit events with edit access.")

    slot_layout_before = (event.start_time, event.recurrence_rule)
    event.update_information(
        title=title,
        description=description,
        event_type=event_type,
        start_time=ensure_aware(start_time) if start_time is not None else None,
        end_time=ensure_aware(end_time) if end_time is not None else None,
        location=location,
        recurrence_rule=(
            RecurrenceRule.create(recurrence_rule)
            if recurrence_rule is not None
            else None
        ),
        recurrence_until=recurrence_until,
        is_all_day=is_all_day,
    )
    event.save()

    # changing the times shifts every slot, so overrides keyed to the old
    # slots would orphan (and render alongside the new occurrences)
    if (event.start_time, event.recurrence_rule) != slot_layout_before:
        event.occurrence_overrides.all().delete()

    resync_event_reminders(event)

    _grant_access(
        event,
        actor=__actor,
        view_grant_targets=view_grant_targets,
        edit_grant_targets=edit_grant_targets,
    )

    return event


@use_case
def delete_event(
    __actor: OrgUser,
    event_uuid: UUID,
) -> None:
    event = CalendarEvent.objects.get(uuid=event_uuid)
    if not event.has_edit_access(__actor):
        raise DomainError("You can only delete events with edit access.")
    event.delete()
