from typing import List

from django.core.exceptions import ObjectDoesNotExist

from apps.core.auth.models import RlcUser
from apps.core.events.models import Event
from apps.core.events.types.schemas import (
    EventCreate,
    EventDelete,
    EventResponse,
    EventUpdate,
)
from apps.core.rlc.models import Org
from apps.static.api_layer import Router
from apps.static.service_layer import ServiceResult

router = Router()

LIST_EVENTS_SUCCESS = "User {} has requested the list of all his events."
CREATE_EVENT_SUCCESS = "User {} has created a new event."

UPDATE_EVENT_SUCCESS = "User {} has updated an event."
UPDATE_EVENT_NOT_FOUND = "User {} tried to edit an event that does not exist."
UPDATE_EVENT_ERROR_UNAUTHORIZED = (
    "User {} tried to update an event that is not part of his clinic."
)

DELETE_EVENT_SUCCESS = "User {} successfully deleted an event."
DELETE_EVENT_NOT_FOUND = "User {} tried to delete an event that does not exist."
DELETE_EVENT_ERROR_UNAUTHORIZED = (
    "User {} tried to delete an event that is not part of his clinic."
)


@router.api(output_schema=List[EventResponse], auth=True)
def get_all_events_for_user(rlc_user: RlcUser):
    events: List[EventResponse] = Event.get_all_events_for_user(rlc_user)
    return ServiceResult(LIST_EVENTS_SUCCESS, events)


@router.api(
    method="POST", input_schema=EventCreate, output_schema=EventResponse, auth=True
)
def create_event(data: EventCreate, rlc_user: RlcUser):  # TODO: Owner?
    org_list = Org.objects.filter(id=rlc_user.org.id)
    event = org_list[0].events.create(
        is_global=data.is_global,
        name=data.name,
        description=data.description,
        start_time=data.start_time,
        end_time=data.end_time,
    )
    return ServiceResult(CREATE_EVENT_SUCCESS, event)


@router.api(
    url="<int:id>/",
    method="PUT",
    input_schema=EventUpdate,
    output_schema=EventResponse,
    auth=True,
)
def update_event(data: EventUpdate, rlc_user: RlcUser):
    try:
        event = Event.objects.get(id=data.id)
    except ObjectDoesNotExist:
        return ServiceResult(
            UPDATE_EVENT_NOT_FOUND, error="The event you want to edit does not exist."
        )

    if rlc_user.org.id != event.org.id:
        return ServiceResult(
            UPDATE_EVENT_ERROR_UNAUTHORIZED,
            error="You do not have the permission to edit this event.",
        )

    event.update_information(data)

    return ServiceResult(UPDATE_EVENT_SUCCESS, event)


@router.api(url="<int:id>/", method="DELETE", input_schema=EventDelete)
def delete_event(data: EventDelete, rlc_user: RlcUser):
    try:
        event = Event.objects.get(id=data.id)
    except ObjectDoesNotExist:
        return ServiceResult(
            DELETE_EVENT_NOT_FOUND, error="The event you want to delete does not exist."
        )
    if rlc_user.org.id != event.org.id:
        return ServiceResult(
            DELETE_EVENT_ERROR_UNAUTHORIZED,
            error="You do not have the permission to delete this event.",
        )

    event.delete()
    return ServiceResult(DELETE_EVENT_SUCCESS)
