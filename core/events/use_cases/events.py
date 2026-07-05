from datetime import datetime

import bleach

from core.auth.models.org_user import OrgUser
from core.events.models.event import EventsEvent
from core.org.models.org import Org
from core.seedwork.use_case_layer import UseCaseError, use_case

MAX_EVENT_NAME_LENGTH = 200
MAX_EVENT_LEVEL_LENGTH = 200


def _validate_max_length(value: str, field_name: str, max_length: int):
    if len(value) > max_length:
        raise UseCaseError(
            f"{field_name} is too long. Maximum length is {max_length} characters."
        )


@use_case
def create_event(
    __actor: OrgUser,
    description: str,
    level: str,
    name: str,
    start_time: datetime,
    end_time: datetime,
):
    _validate_max_length(name, "Name", MAX_EVENT_NAME_LENGTH)
    _validate_max_length(level, "Level", MAX_EVENT_LEVEL_LENGTH)

    org = Org.objects.get(id=__actor.org.pk)
    event = EventsEvent.create(
        org=org,
        name=name,
        description=description,
        level=level,
        start_time=start_time,
        end_time=end_time,
    )
    event.save()
    return event


@use_case
def update_event(
    __actor: OrgUser,
    event_id: int,
    description: str,
    name: str,
    start_time: datetime,
    end_time: datetime,
):
    _validate_max_length(name, "Name", MAX_EVENT_NAME_LENGTH)

    event = EventsEvent.objects.get(id=event_id)

    if __actor.org.pk != event.org.pk:
        raise UseCaseError(
            "You do not have the permission to edit this event.",
        )

    if description is not None:
        description = bleach.clean(
            description,
            tags=["a", "p", "strong", "em", "ul", "ol", "li", "s"],
            attributes={"a": ["href"]},
        )

    event.update_information(
        description=description,
        name=name,
        start_time=start_time,
        end_time=end_time,
    )

    event.save()

    return event


@use_case
def delete_event(__actor: OrgUser, event_id: int):
    event = EventsEvent.objects.get(id=event_id)

    if __actor.org.pk != event.org.pk:
        raise UseCaseError(
            "You do not have the permission to delete this event.",
        )

    event.delete()


@use_case
def reset_calendar_uuid(__actor: OrgUser):
    __actor.regenerate_calendar_uuid()
