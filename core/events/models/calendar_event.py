from datetime import date, datetime
from uuid import uuid4

from django.db import models

from core.auth.models import OrgUser
from core.seedwork.domain_layer import DomainError


class RecurrenceRule(str):
    def __new__(cls, value: str = ""):
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise TypeError("RecurrenceRule must be a string.")

        normalized = value.strip()
        if len(normalized) > 200:
            raise DomainError("Recurrence rule must be at most 200 characters.")

        return str.__new__(cls, normalized)

    @classmethod
    def create(cls, value: str | None = None) -> "RecurrenceRule":
        if value is None:
            return cls("")
        return cls(value)


class CalendarEvent(models.Model):
    class EventType(models.TextChoices):
        APPOINTMENT = "APPOINTMENT", "Appointment"
        TASK = "TASK", "Task"
        MEETING = "MEETING", "Meeting"
        DEADLINE = "DEADLINE", "Deadline"
        EXTERNAL = "EXTERNAL", "External"

    uuid = models.UUIDField(default=uuid4, unique=True, editable=False)
    creator = models.ForeignKey(
        OrgUser, on_delete=models.CASCADE, related_name="calendar_events"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=500, blank=True, default="")
    recurrence_rule = models.CharField(max_length=200, blank=True, default="")
    recurrence_until = models.DateField(null=True, blank=True)
    guest_users: models.ManyToManyField["OrgUser", "CalendarEventGuest"] = (
        models.ManyToManyField(
            OrgUser,
            through="CalendarEventGuest",
            related_name="guest_at_events",
            blank=True,
        )
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "EVT_CalendarEvent"
        ordering = ["start_time"]

    @classmethod
    def create(
        cls,
        creator: OrgUser,
        title: str,
        event_type: "CalendarEvent.EventType",
        start_time: datetime,
        end_time: datetime | None = None,
        description: str = "",
        location: str = "",
        recurrence_rule: RecurrenceRule | None = None,
        recurrence_until: date | None = None,
    ) -> "CalendarEvent":
        if end_time is not None and start_time > end_time:
            raise DomainError("The start time must be before the end time.")
        return cls(
            creator=creator,
            title=title,
            event_type=event_type,
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=location,
            recurrence_rule=str(recurrence_rule) if recurrence_rule is not None else "",
            recurrence_until=recurrence_until,
        )

    @staticmethod
    def get_all_events_for_user(org_user: OrgUser) -> models.QuerySet["CalendarEvent"]:
        return CalendarEvent.objects.filter(creator=org_user)

    def update_information(
        self,
        title: str | None = None,
        description: str | None = None,
        event_type: "CalendarEvent.EventType | None" = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        location: str | None = None,
        recurrence_rule: RecurrenceRule | None = None,
        recurrence_until: date | None = None,
    ) -> None:
        new_start = start_time if start_time is not None else self.start_time
        new_end = end_time if end_time is not None else self.end_time
        if new_end is not None and new_start > new_end:
            raise DomainError("The start time must be before the end time.")

        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if event_type is not None:
            self.event_type = event_type
        if start_time is not None:
            self.start_time = start_time
        if end_time is not None:
            self.end_time = end_time
        if location is not None:
            self.location = location
        if recurrence_rule is not None:
            self.recurrence_rule = recurrence_rule
        if recurrence_until is not None:
            self.recurrence_until = recurrence_until


class CalendarEventGuest(models.Model):
    class AttendanceStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        DECLINED = "DECLINED", "Declined"

    event = models.ForeignKey(
        CalendarEvent, on_delete=models.CASCADE, related_name="guests"
    )
    org_user = models.ForeignKey(
        OrgUser, on_delete=models.CASCADE, related_name="guest_events"
    )
    attendance_status = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PENDING,
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("event", "org_user")]
        verbose_name = "EVT_CalendarEventGuest"


class CalendarEventAttachment(models.Model):
    event = models.ForeignKey(
        CalendarEvent, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(upload_to="calendar/attachments/")
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "EVT_CalendarEventAttachment"
