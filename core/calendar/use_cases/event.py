from datetime import date, datetime
from uuid import UUID

from django.db import transaction

from core.auth.models.org_user import OrgUser
from core.calendar.models import CalendarEvent, CalendarEventShare, RecurrenceRule
from core.org.models import Group
from core.seedwork.domain_layer import DomainError
from core.seedwork.use_case_layer import use_case
from core.seedwork.use_case_layer.error import UseCaseError

from seedwork.functional import list_filter, list_map


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
    view_grant_targets: list[str] | None,
    edit_grant_targets: list[str] | None,
) -> None:
    if view_grant_targets is None and edit_grant_targets is None:
        return

    user_view_access = list_map(
        list_filter(view_grant_targets or [], lambda t: t.startswith("user:")),
        lambda t: _parse_grant_target(t)[1],
    )
    group_view_access = list_map(
        list_filter(view_grant_targets or [], lambda t: t.startswith("group:")),
        lambda t: _parse_grant_target(t)[1],
    )
    org_view_access = list_map(
        list_filter(view_grant_targets or [], lambda t: t.startswith("org:")),
        lambda t: _parse_grant_target(t)[1],
    )

    user_edit_access = list_map(
        list_filter(edit_grant_targets or [], lambda t: t.startswith("user:")),
        lambda t: _parse_grant_target(t)[1],
    )
    group_edit_access = list_map(
        list_filter(edit_grant_targets or [], lambda t: t.startswith("group:")),
        lambda t: _parse_grant_target(t)[1],
    )
    org_edit_access = list_map(
        list_filter(edit_grant_targets or [], lambda t: t.startswith("org:")),
        lambda t: _parse_grant_target(t)[1],
    )

    with transaction.atomic():
        event.shares.exclude(shared_user=event.creator).delete()

        for user_id in user_view_access:
            event.grant_access(
                by=actor,
                access_level=CalendarEventShare.AccessLevel.VIEW,
                shared_user=OrgUser.objects.get(pk=user_id),
            )

        for user_id in user_edit_access:
            event.grant_access(
                by=actor,
                access_level=CalendarEventShare.AccessLevel.EDIT,
                shared_user=OrgUser.objects.get(pk=user_id),
            )

        for group_id in group_view_access:
            event.grant_access(
                by=actor,
                access_level=CalendarEventShare.AccessLevel.VIEW,
                shared_group=Group.objects.get(pk=group_id),
            )

        for group_id in group_edit_access:
            event.grant_access(
                by=actor,
                access_level=CalendarEventShare.AccessLevel.EDIT,
                shared_group=Group.objects.get(pk=group_id),
            )

        if org_view_access:
            event.grant_access(
                by=actor,
                access_level=CalendarEventShare.AccessLevel.VIEW,
                shared_org=actor.org,
            )

        if org_edit_access:
            event.grant_access(
                by=actor,
                access_level=CalendarEventShare.AccessLevel.EDIT,
                shared_org=actor.org,
            )


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
    view_grant_targets: list[str] | None = None,
    edit_grant_targets: list[str] | None = None,
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
        view_grant_targets=view_grant_targets,
        edit_grant_targets=edit_grant_targets,
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
