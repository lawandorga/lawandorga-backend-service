import uuid

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from core.auth.models import RlcUser
from core.events.api.schemas import CalendarUuidUser
from core.seedwork.api_layer import Router

router = Router()


def get_ics_calendar(request, calendar_uuid: uuid.UUID):
    user = get_object_or_404(RlcUser, calendar_uuid=calendar_uuid)
    calendar = user.get_ics_calendar()
    return HttpResponse(calendar, content_type="text/calendar")


@router.get(output_schema=CalendarUuidUser)
def get_calender_uuid(rlc_user: RlcUser):
    return {"id": rlc_user.id, "calendar_uuid": rlc_user.calendar_uuid}
