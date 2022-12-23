from typing import List

from django.core.exceptions import ObjectDoesNotExist

from core.auth.models import RlcUser
from core.events.api.schemas import (
    InputAttendanceUpdate, InputAttendanceCreate, InputAttendanceDelete, OutputAttendanceResponse
)
from core.events.models import Event
from core.events.models.attendance import Attendance
from core.events.use_cases.attendances import create_attendance, update_attendance, delete_attendance
from core.rlc.models import Org
from core.seedwork.api_layer import ApiError, Router

router = Router()


@router.api(output_schema=List[OutputAttendanceResponse])
def get_all_attendances_for_user(rlc_user: RlcUser):
    attendances: List[OutputAttendanceResponse] = Attendance.get_all_attendances_for_user(rlc_user)
    return attendances


@router.post(
    input_schema=InputAttendanceCreate,
)
def command__create_attendance(data: InputAttendanceCreate, rlc_user: RlcUser):
    create_attendance(rlc_user, data.status, data.event_id)


@router.api(
    url="<int:id>/",
    method="PUT",
    input_schema=InputAttendanceUpdate,
)
def command__update_attendance(data: InputAttendanceUpdate, rlc_user: RlcUser):
    update_attendance(rlc_user, data.status, attendance=data.id)


@router.delete(url="<int:id>/", input_schema=InputAttendanceDelete)
def command__delete_attendance(data: InputAttendanceDelete, rlc_user: RlcUser):
    delete_attendance(rlc_user, data.id)
