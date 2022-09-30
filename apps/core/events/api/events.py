from typing import List

from apps.core.auth.models import RlcUser
from apps.core.events.api.schemas import EventCreate, EventResponse
from apps.core.events.models import Event
from apps.core.rlc.models import Org
from apps.static.api_layer import Router
from apps.static.service_layer import ServiceResult

router = Router()

LIST_EVENTS_SUCCESS = "User {} has requested the list of all his events."
CREATE_EVENT_SUCCESS = "User {} has created a new event."


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
