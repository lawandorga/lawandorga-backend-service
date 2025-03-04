import uuid

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from pydantic import BaseModel

from core.auth.models import OrgUser
from core.seedwork.api_layer import Router

router = Router()


def get_ics_calendar(request, calendar_uuid: uuid.UUID):
    user = get_object_or_404(OrgUser, calendar_uuid=calendar_uuid)
    calendar = user.get_ics_calendar()
    return HttpResponse(calendar, content_type="text/calendar")


class CalendarUuidUser(BaseModel):
    id: int
    calendar_uuid: uuid.UUID
    calendar_url: str


@router.get(output_schema=CalendarUuidUser)
def get_calender_uuid(org_user: OrgUser):
    return {
        "id": org_user.pk,
        "calendar_uuid": org_user.calendar_uuid,
        "calendar_url": f"{settings.CALENDAR_URL}{org_user.calendar_uuid}.ics",
    }
