import uuid

from django.conf import settings
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
    return {
        "id": rlc_user.id,
        "calendar_uuid": rlc_user.calendar_uuid,
        "calendar_url": f"{settings.CALENDAR_URL}{rlc_user.calendar_uuid}.ics",
    }


@router.post(url="reset/", output_schema=CalendarUuidUser)
def reset_calendar_uuid(rlc_user: RlcUser):
    rlc_user.regenerate_calendar_uuid()
    return {
        "id": rlc_user.id,
        "calendar_uuid": rlc_user.calendar_uuid,
        "calendar_url": f"{settings.CALENDAR_URL}{rlc_user.calendar_uuid}.ics",
    }
