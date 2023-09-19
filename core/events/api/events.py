import bleach
from django.core.exceptions import ObjectDoesNotExist

from core.auth.models import RlcUser
from core.events.api.schemas import (
    InputEventCreate,
    InputEventDelete,
    InputEventUpdate,
    OutputEventResponse,
)
from core.events.models import EventsEvent
from core.rlc.models import Org
from core.seedwork.api_layer import ApiError, Router

router = Router()


@router.api(output_schema=list[OutputEventResponse])
def get_all_events_for_user(rlc_user: RlcUser):
    return list(EventsEvent.get_all_events_for_user(rlc_user))


@router.post()
def create_event(data: InputEventCreate, rlc_user: RlcUser):
    org = Org.objects.get(id=rlc_user.org.pk)
    clean_description = bleach.clean(
        data.description,
        tags=["a", "p", "strong", "em", "ul", "ol", "li", "s"],
        attributes={"a": ["href"]},
    )
    event = org.events.create(
        level=data.level,
        name=data.name,
        description=clean_description,
        start_time=data.start_time,
        end_time=data.end_time,
    )
    return event


@router.put(url="<int:id>/")
def update_event(data: InputEventUpdate, rlc_user: RlcUser):
    try:
        event = EventsEvent.objects.get(id=data.id)
    except ObjectDoesNotExist:
        raise ApiError("The event you want to edit does not exist.")

    if rlc_user.org.pk != event.org.pk:
        raise ApiError(
            "You do not have the permission to edit this event.",
        )

    if data.description is not None:
        data.description = bleach.clean(
            data.description,
            tags=["a", "p", "strong", "em", "ul", "ol", "li", "s"],
            attributes={"a": ["href"]},
        )
    update_data = data.model_dump()
    update_data.pop("id")
    event.update_information(**update_data)

    return event


@router.delete(url="<int:id>/")
def delete_event(data: InputEventDelete, rlc_user: RlcUser):
    try:
        event = EventsEvent.objects.get(id=data.id)
    except ObjectDoesNotExist:
        raise ApiError("The event you want to delete does not exist.")
    if rlc_user.org.pk != event.org.pk:
        raise ApiError(
            "You do not have the permission to delete this event.",
        )

    event.delete()
