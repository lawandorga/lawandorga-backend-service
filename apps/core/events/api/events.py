from datetime import datetime
from typing import List

from pydantic import BaseModel

from apps.core.auth.models import RlcUser
from apps.core.events.models import Event
from apps.core.rlc.models import Org
from apps.static.api_layer import Router
from apps.static.service_layer import ServiceResult

router = Router()


class EventResponse(BaseModel):
    id: int
    created: datetime
    updated: datetime
    is_global: bool
    name: str
    description: str
    start_time: datetime
    end_time: datetime
    # TODO: org is missing


LIST_EVENTS_SUCCESS = "User {} has requested the list of all his events."


@router.api(output_schema=List[EventResponse], auth=True)
def get_all_events_for_user(rlc_user: RlcUser):
    events: List[EventResponse] = Event.get_all_events_for_user(rlc_user)
    return ServiceResult(LIST_EVENTS_SUCCESS, events)
