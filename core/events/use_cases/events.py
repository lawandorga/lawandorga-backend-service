from datetime import datetime

import bleach
from django.core.exceptions import ObjectDoesNotExist

from core.auth.models.org_user import OrgUser
from core.events.models.event import EventsEvent
from core.rlc.models.org import Org
from core.seedwork.use_case_layer import UseCaseError, use_case


@use_case
def create_event(
    __actor: OrgUser,
    description: str,
    level: str,
    name: str,
    start_time: datetime,
    end_time: datetime,
):
    org = Org.objects.get(id=__actor.org.pk)
    clean_description = bleach.clean(
        description,
        tags=["a", "p", "strong", "em", "ul", "ol", "li", "s"],
        attributes={"a": ["href"]},
    )
    event = org.events.create(
        level=level,
        name=name,
        description=clean_description,
        start_time=start_time,
        end_time=end_time,
    )
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
    try:
        event = EventsEvent.objects.get(id=event_id)
    except ObjectDoesNotExist:
        raise UseCaseError("The event you want to edit does not exist.")

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

    return event


@use_case
def delete_event(__actor: OrgUser, event_id: int):
    try:
        event = EventsEvent.objects.get(id=event_id)
    except ObjectDoesNotExist:
        raise UseCaseError("The event you want to delete does not exist.")
    if __actor.org.pk != event.org.pk:
        raise UseCaseError(
            "You do not have the permission to delete this event.",
        )

    event.delete()


@use_case
def reset_calendar_uuid(__actor: OrgUser):
    __actor.regenerate_calendar_uuid()
