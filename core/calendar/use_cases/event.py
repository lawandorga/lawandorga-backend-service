from datetime import date, datetime
from uuid import UUID

from core.auth.models.org_user import OrgUser
from core.calendar.models import CalendarEvent, CalendarEventShare, RecurrenceRule
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


def _grant_access(
    event: CalendarEvent,
    *,
    actor: OrgUser,
    access_level: CalendarEventShare.AccessLevel,
    grant_targets: list[str] | None,
) -> None:
    if grant_targets is None:
        return

    wanted_user_ids: set[int] = set()
    wanted_group_ids: set[int] = set()
    wanted_org = False

    for target in grant_targets:
        target_type, target_id = _parse_grant_target(target)

        if target_type == "user":
            wanted_user_ids.add(target_id)
        elif target_type == "group":
            wanted_group_ids.add(target_id)
        elif target_type == "org":
            if target_id != actor.org_id:
                raise DomainError("Org grant target must match your own org.")
            wanted_org = True
    current_user_ids = set(
        event.shares.filter(shared_user__isnull=False)
        .exclude(shared_user=event.creator)
        .values_list("shared_user_id", flat=True)
    )
    for user_id in current_user_ids - wanted_user_ids:
        event.revoke_access(shared_user=OrgUser.objects.get(pk=user_id))
    for user_id in wanted_user_ids:
        event.grant_access(
            by=actor,
            access_level=access_level,
            shared_user=OrgUser.objects.get(pk=user_id),
        )

    current_group_ids = set(
        event.shares.filter(shared_group__isnull=False).values_list(
            "shared_group_id", flat=True
        )
    )
    for group_id in current_group_ids - wanted_group_ids:
        event.revoke_access(shared_group=Group.objects.get(pk=group_id))
    for group_id in wanted_group_ids:
        event.grant_access(
            by=actor,
            access_level=access_level,
            shared_group=Group.objects.get(pk=group_id),
        )

    has_org_share = event.shares.filter(shared_org=actor.org).exists()
    if wanted_org:
        event.grant_access(
            by=actor,
            access_level=access_level,
            shared_org=actor.org,
        )
    elif has_org_share:
        event.revoke_access(shared_org=actor.org)


def _has_share_changes(*, grant_targets: list[str] | None) -> bool:
    return grant_targets is not None


@use_case
def create_event(
    __actor: OrgUser,
    title: str,
    event_type: CalendarEvent.EventType,
    start_time: datetime,
    end_time: datetime,
    description: str | None = None,
    location: str | None = None,
    recurrence_rule: str | None = None,
    recurrence_until: date | None = None,
    is_all_day: bool = False,
    grant_targets: list[str] | None = None,
    grant_access_level: CalendarEventShare.AccessLevel = CalendarEventShare.AccessLevel.VIEW,
) -> CalendarEvent:
    event = CalendarEvent.create(
        creator=__actor,
        title=title,
        event_type=event_type,
        start_time=start_time,
        end_time=end_time,
        description=description or "",
        location=location or "",
        recurrence_rule=RecurrenceRule.create(recurrence_rule),
        recurrence_until=recurrence_until,
        is_all_day=is_all_day,
    )
    event.save()
    _grant_access(
        event,
        actor=__actor,
        access_level=grant_access_level,
        grant_targets=grant_targets,
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
    grant_targets: list[str] | None = None,
    grant_access_level: CalendarEventShare.AccessLevel = CalendarEventShare.AccessLevel.VIEW,
) -> CalendarEvent:
    event = CalendarEvent.objects.get(uuid=event_uuid)

    if not event.has_edit_access(__actor):
        raise DomainError("You can only edit events with edit access.")

    if _has_share_changes(grant_targets=grant_targets) and not event.has_admin_access(
        __actor
    ):
        raise DomainError("You can only change event shares with admin access.")

    old_start_time = event.start_time
    event.update_information(
        title=title,
        description=description,
        event_type=event_type,
        start_time=start_time,
        end_time=end_time,
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

    start_time_changed = start_time is not None and start_time != old_start_time
    if start_time_changed:
        event.reschedule_reminders()

    _grant_access(
        event,
        actor=__actor,
        access_level=grant_access_level,
        grant_targets=grant_targets,
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
