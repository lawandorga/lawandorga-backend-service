from typing import List

from django.core.exceptions import ObjectDoesNotExist

from core.auth.models import RlcUser
from core.events.api.schemas import (
    InputEventCreate,
    InputEventDelete,
    InputEventUpdate,
    OutputEventResponse, OutputAttendanceResponse, InputAttendanceUpdate,
)
from core.events.models import Event
from core.events.models.attendance import Attendance
from core.rlc.models import Org
from core.seedwork.api_layer import ApiError, Router

router = Router()


@router.api(output_schema=List[OutputAttendanceResponse])
def get_all_attendances_for_user(rlc_user: RlcUser):
    attendances: List[OutputAttendanceResponse] = Attendance.get_all_attendances_for_user(rlc_user)
    return attendances


# TODO: Only update should be needed. Maybe needed for initial attendance table creation tho
"""@router.api(
    method="POST",
    input_schema=InputEventCreate,
)
def create_event(data: InputEventCreate, rlc_user: RlcUser):
    org_list = Org.objects.filter(id=rlc_user.org.id)
    event = org_list[0].events.create(
        is_global=data.is_global,
        name=data.name,
        description=data.description,
        start_time=data.start_time,
        end_time=data.end_time,
    )
    return event"""


@router.api(
    url="<int:id>/",  # TODO: How to handle this? Which Attendance should be updated?
    method="PUT",
    input_schema=InputAttendanceUpdate,
    output_schema=OutputAttendanceResponse,
)
def update_event(data: InputAttendanceUpdate, rlc_user: RlcUser):
    try:
        # TODO: Schema requires event_id for get, but event should be immutable. What to do?
        attendance = Attendance.objects.get(rlc_user=rlc_user, event=data.event_id)
    except ObjectDoesNotExist:
        raise ApiError("You are not invited to this event.")

    update_data = data.dict()
    if update_data["event_id"] != attendance.event:
        raise ApiError("Event ID is not changeable.")
    attendance.update_information(**update_data)  # user and event should be immutable

    return attendance


"""@router.api(url="<int:id>/", method="DELETE", input_schema=InputEventDelete)
def delete_event(data: InputEventDelete, rlc_user: RlcUser):
    try:
        event = Event.objects.get(id=data.id)
    except ObjectDoesNotExist:
        raise ApiError("The event you want to delete does not exist.")
    if rlc_user.org.id != event.org.id:
        raise ApiError(
            "You do not have the permission to delete this event.",
        )

    event.delete()"""
