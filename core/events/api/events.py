from datetime import datetime

from django.utils.timezone import localtime
from pydantic import BaseModel, ConfigDict, field_validator

from core.auth.models import OrgUser
from core.events.models import EventsEvent
from core.seedwork.api_layer import Router

router = Router()


class OutputRlc(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class OutputEventResponse(BaseModel):
    id: int
    created: datetime
    updated: datetime
    is_global: bool
    name: str
    description: str
    start_time: datetime
    end_time: datetime
    org: OutputRlc
    level: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("start_time", "end_time")
    def format_datetime_validator(cls, v: datetime) -> datetime:
        v = localtime(v)
        return v


@router.api(output_schema=list[OutputEventResponse])
def get_all_events_for_user(org_user: OrgUser):
    return list(EventsEvent.get_all_events_for_user(org_user))
