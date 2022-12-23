from django.db import transaction

from core.auth.models import RlcUser
from core.events.models import Event, Attendance
from core.events.use_cases.finders import event_from_id, attendance_from_id
from core.seedwork.use_case_layer import use_case, find


@use_case
def create_attendance(__actor: RlcUser, status: str, event=find(event_from_id)):
    attendance = Attendance(event=event, rlc_user=__actor, status=status)
    attendance.save()


@use_case
def update_attendance(__actor: RlcUser, a: str, attendance=find(attendance_from_id)):
    attendance.update_information(attendance=a)
    attendance.save()


@use_case
def delete_attendance(__actor: RlcUser, attendance=find(attendance_from_id)):
    attendance.delete()
