from typing import List

from django.db import models

from core.auth.models import RlcUser
from core.events.models import Event


class Attendance(models.Model):
    event = models.ForeignKey(Event, related_name="attendances", on_delete=models.PROTECT)
    rlc_user = models.ForeignKey(RlcUser, related_name="users", on_delete=models.PROTECT)  # Maybe "Attendees" would
    # be a better related name
    ATTENDING = 'Y'  # Yes
    UNSURE = 'U'  # Unsure
    ABSENT = 'N'  # No
    ATTENDANCE_CHOICES = [
        (ATTENDING, 'Attending'),
        (UNSURE, 'Unsure'),
        (ABSENT, 'Absent')
    ]
    status = models.CharField(
        choices=ATTENDANCE_CHOICES,
        default=UNSURE,
        max_length=1
    )

    @staticmethod
    def get_all_attendances_for_user(rlc_user: RlcUser):
        raw_attendances: List[Attendance] = (
            list(
                Attendance.objects.filter(rlc_user=rlc_user)
            )
        )
        return raw_attendances

    @staticmethod
    def get_all_attendances_for_event(event: Event):
        raw_attendances: List[Attendance] = (
            list(
                Attendance.objects.filter(event=event)
            )
        )
        return raw_attendances

    def update_information(
        self,
        attendance=None
    ):
        self.status = attendance
