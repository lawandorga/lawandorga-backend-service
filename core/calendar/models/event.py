from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from django.db import models
from django.db.models import Q
from django.utils import timezone

from core.auth.models import OrgUser
from core.seedwork.domain_layer import DomainError

if TYPE_CHECKING:
    from core.org.models import Group, Org


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
    end_time = models.DateTimeField()
    is_all_day = models.BooleanField(default=False)
    location = models.CharField(max_length=500, blank=True, default="")
    recurrence_rule = models.CharField(max_length=200, blank=True, default="")
    recurrence_until = models.DateField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        shares: models.QuerySet["CalendarEventShare"]
        reminders: models.QuerySet["CalendarEventReminder"]

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
        end_time: datetime,
        description: str = "",
        location: str = "",
        recurrence_rule: RecurrenceRule | None = None,
        recurrence_until: date | None = None,
        is_all_day: bool = False,
    ) -> "CalendarEvent":
        if start_time > end_time:
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
            is_all_day=is_all_day,
        )

    @staticmethod
    def get_accessible_events_for_user(
        org_user: OrgUser,
    ) -> models.QuerySet["CalendarEvent"]:
        share_filter = (
            Q(shares__shared_user=org_user)
            | Q(shares__shared_group__members=org_user)
            | Q(shares__shared_org=org_user.org)
        )
        return (
            CalendarEvent.objects.filter(Q(creator=org_user) | share_filter)
            .distinct()
            .order_by("start_time")
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        share, created = CalendarEventShare.objects.get_or_create(
            event=self,
            shared_user=self.creator,
            defaults={
                "access_level": CalendarEventShare.AccessLevel.ADMIN,
                "granted_by": self.creator,
            },
        )
        if not created and share.access_level != CalendarEventShare.AccessLevel.ADMIN:
            share.access_level = CalendarEventShare.AccessLevel.ADMIN
            share.granted_by = self.creator
            share.save(update_fields=["access_level", "granted_by"])

    @property
    def creator_id(self) -> int:
        return self.creator.pk

    @property
    def creator_name(self) -> str:
        return self.creator.name

    @property
    def guest_user_ids(self) -> list[int]:
        return list(
            self.shares.filter(shared_user__isnull=False)
            .exclude(shared_user=self.creator)
            .values_list("shared_user_id", flat=True)
            .distinct()
        )

    @property
    def guest_user_names(self) -> list[str]:
        return list(
            self.shares.filter(shared_user__isnull=False)
            .exclude(shared_user=self.creator)
            .values_list("shared_user__user__name", flat=True)
            .distinct()
        )

    @property
    def grant_targets(self) -> list[str]:
        targets: list[str] = []

        user_ids = (
            self.shares.filter(shared_user__isnull=False)
            .exclude(shared_user=self.creator)
            .values_list("shared_user_id", flat=True)
            .distinct()
        )
        for user_id in user_ids:
            if user_id is not None:
                targets.append(f"user:{user_id}")

        group_ids = (
            self.shares.filter(shared_group__isnull=False)
            .values_list("shared_group_id", flat=True)
            .distinct()
        )
        for group_id in group_ids:
            if group_id is not None:
                targets.append(f"group:{group_id}")

        org_ids = (
            self.shares.filter(shared_org__isnull=False)
            .values_list("shared_org_id", flat=True)
            .distinct()
        )
        for org_id in org_ids:
            if org_id is not None:
                targets.append(f"org:{org_id}")

        return targets

    def has_view_access(self, org_user: OrgUser) -> bool:
        if self.creator_id == org_user.pk:
            return True
        return self.shares.filter(
            Q(shared_user=org_user)
            | Q(shared_group__members=org_user)
            | Q(shared_org=org_user.org)
        ).exists()

    def has_edit_access(self, org_user: OrgUser) -> bool:
        if self.creator_id == org_user.pk:
            return True
        return self.shares.filter(
            Q(shared_user=org_user)
            | Q(shared_group__members=org_user)
            | Q(shared_org=org_user.org),
            access_level__in=[
                CalendarEventShare.AccessLevel.EDIT,
                CalendarEventShare.AccessLevel.ADMIN,
            ],
        ).exists()

    def has_admin_access(self, org_user: OrgUser) -> bool:
        if self.creator_id == org_user.pk:
            return True
        return self.shares.filter(
            Q(shared_user=org_user)
            | Q(shared_group__members=org_user)
            | Q(shared_org=org_user.org),
            access_level=CalendarEventShare.AccessLevel.ADMIN,
        ).exists()

    def grant_access(
        self,
        *,
        by: OrgUser,
        access_level: "CalendarEventShare.AccessLevel | None" = None,
        shared_user: OrgUser | None = None,
        shared_group: "Group | None" = None,
        shared_org: "Org | None" = None,
    ) -> "CalendarEventShare":
        access_level = access_level or CalendarEventShare.AccessLevel.VIEW
        principal_count = sum(
            [
                1 if shared_user is not None else 0,
                1 if shared_group is not None else 0,
                1 if shared_org is not None else 0,
            ]
        )
        if principal_count != 1:
            raise DomainError("Exactly one share target must be provided.")

        event_org_id = self.creator.org_id
        if shared_user is not None and shared_user.org_id != event_org_id:
            raise DomainError("Shared user must be in the same org as the event.")
        if shared_group is not None and shared_group.org_id != event_org_id:
            raise DomainError("Shared group must be in the same org as the event.")
        if shared_org is not None and shared_org.pk != event_org_id:
            raise DomainError("Shared org must match the event org.")
        if (
            shared_user is not None
            and shared_user.pk == self.creator_id
            and access_level != CalendarEventShare.AccessLevel.ADMIN
        ):
            raise DomainError("The creator share must always be ADMIN.")

        share, created = CalendarEventShare.objects.get_or_create(
            event=self,
            shared_user=shared_user,
            shared_group=shared_group,
            shared_org=shared_org,
            defaults={
                "access_level": access_level,
                "granted_by": by,
            },
        )
        if not created:
            share.access_level = access_level
            share.granted_by = by
            share.save(update_fields=["access_level", "granted_by"])
        return share

    def revoke_access(
        self,
        *,
        shared_user: OrgUser | None = None,
        shared_group: "Group | None" = None,
        shared_org: "Org | None" = None,
    ) -> bool:
        principal_count = sum(
            [
                1 if shared_user is not None else 0,
                1 if shared_group is not None else 0,
                1 if shared_org is not None else 0,
            ]
        )
        if principal_count != 1:
            raise DomainError("Exactly one share target must be provided.")

        share = CalendarEventShare.objects.filter(
            event=self,
            shared_user=shared_user,
            shared_group=shared_group,
            shared_org=shared_org,
        ).first()
        if share is None:
            return False
        share.delete()
        return True

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
        is_all_day: bool | None = None,
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
            self.recurrence_until = recurrence_until
        if is_all_day is not None:
            self.is_all_day = is_all_day

    def reschedule_reminders(self) -> None:
        for reminder in self.reminders.all():
            reminder.reschedule(self.start_time)

    def __str__(self):
        return f"CalendarEvent: {self.pk}, title: {self.title}, creator: {self.creator.name}"


class CalendarEventAttachment(models.Model):
    event = models.ForeignKey(
        CalendarEvent, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(upload_to="calendar/attachments/")
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "EVT_CalendarEventAttachment"


class CalendarEventShare(models.Model):
    class AccessLevel(models.TextChoices):
        VIEW = "VIEW", "View"
        EDIT = "EDIT", "Edit"
        ADMIN = "ADMIN", "Admin"

    event = models.ForeignKey(
        CalendarEvent, on_delete=models.CASCADE, related_name="shares"
    )
    shared_user = models.ForeignKey(
        OrgUser,
        on_delete=models.CASCADE,
        related_name="calendar_event_user_shares",
        null=True,
        blank=True,
    )
    shared_group = models.ForeignKey(
        "Group",
        on_delete=models.CASCADE,
        related_name="calendar_event_group_shares",
        null=True,
        blank=True,
    )
    shared_org = models.ForeignKey(
        "Org",
        on_delete=models.CASCADE,
        related_name="calendar_event_org_shares",
        null=True,
        blank=True,
    )
    access_level = models.CharField(
        max_length=20,
        choices=AccessLevel.choices,
        default=AccessLevel.VIEW,
    )
    granted_by = models.ForeignKey(
        OrgUser,
        on_delete=models.SET_NULL,
        related_name="granted_calendar_event_shares",
        null=True,
        blank=True,
    )
    created = models.DateTimeField(auto_now_add=True)

    if TYPE_CHECKING:
        shared_user_id: int | None
        shared_group_id: int | None
        shared_org_id: int | None

    class Meta:
        verbose_name = "EVT_CalendarEventShare"
        constraints = [
            models.CheckConstraint(
                name="calendar_share_exactly_one_principal",
                condition=(
                    (
                        Q(shared_user__isnull=False)
                        & Q(shared_group__isnull=True)
                        & Q(shared_org__isnull=True)
                    )
                    | (
                        Q(shared_user__isnull=True)
                        & Q(shared_group__isnull=False)
                        & Q(shared_org__isnull=True)
                    )
                    | (
                        Q(shared_user__isnull=True)
                        & Q(shared_group__isnull=True)
                        & Q(shared_org__isnull=False)
                    )
                ),
            ),
            models.UniqueConstraint(
                fields=["event", "shared_user"],
                condition=Q(shared_user__isnull=False),
                name="calendar_share_unique_event_user",
            ),
            models.UniqueConstraint(
                fields=["event", "shared_group"],
                condition=Q(shared_group__isnull=False),
                name="calendar_share_unique_event_group",
            ),
            models.UniqueConstraint(
                fields=["event", "shared_org"],
                condition=Q(shared_org__isnull=False),
                name="calendar_share_unique_event_org",
            ),
        ]
        indexes = [
            models.Index(fields=["event", "shared_user"], name="cal_share_user_idx"),
            models.Index(fields=["event", "shared_group"], name="cal_share_group_idx"),
            models.Index(fields=["event", "shared_org"], name="cal_share_org_idx"),
        ]

    @property
    def is_creator_share(self) -> bool:
        return (
            self.shared_user_id is not None
            and self.event.creator_id == self.shared_user_id
        )

    def delete(self, using=None, keep_parents=False):
        if self.is_creator_share:
            raise DomainError("The creator share can not be removed.")
        return super().delete(using=using, keep_parents=keep_parents)


class CalendarEventReminder(models.Model):
    class Method(models.TextChoices):
        EMAIL = "EMAIL", "Email"
        IN_APP = "IN_APP", "In-app"

    uuid = models.UUIDField(default=uuid4, unique=True, editable=False)
    event = models.ForeignKey(
        CalendarEvent, on_delete=models.CASCADE, related_name="reminders"
    )
    org_user = models.ForeignKey(
        OrgUser, on_delete=models.CASCADE, related_name="calendar_event_reminders"
    )
    minutes_before = models.PositiveIntegerField(default=0)
    method = models.CharField(max_length=20, choices=Method.choices)
    remind_at = models.DateTimeField()
    dispatched_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    if TYPE_CHECKING:
        event_id: int
        org_user_id: int

    class Meta:
        verbose_name = "EVT_CalendarEventReminder"
        constraints = [
            models.UniqueConstraint(
                fields=["event", "org_user", "method", "minutes_before"],
                name="calendar_reminder_unique_per_user_method_offset",
            ),
        ]
        indexes = [
            models.Index(
                fields=["remind_at", "dispatched_at"], name="cal_reminder_due_idx"
            ),
        ]

    @staticmethod
    def compute_remind_at(start_time: datetime, minutes_before: int) -> datetime:
        return start_time - timedelta(minutes=minutes_before)

    @classmethod
    def create(
        cls,
        *,
        event: CalendarEvent,
        org_user: OrgUser,
        minutes_before: int,
        method: "CalendarEventReminder.Method",
    ) -> "CalendarEventReminder":
        if minutes_before < 0:
            raise DomainError("A reminder can not fire after the event starts.")
        return cls(
            event=event,
            org_user=org_user,
            minutes_before=minutes_before,
            method=method,
            remind_at=cls.compute_remind_at(event.start_time, minutes_before),
        )

    def reschedule(self, start_time: datetime) -> None:
        self.remind_at = self.compute_remind_at(start_time, self.minutes_before)
        self.dispatched_at = None
        self.save(update_fields=["remind_at", "dispatched_at"])

    def __str__(self):
        return (
            f"CalendarEventReminder: {self.pk}, event: {self.event_id}, "
            f"method: {self.method}, minutes_before: {self.minutes_before}"
        )


class CalendarNotification(models.Model):
    uuid = models.UUIDField(default=uuid4, unique=True, editable=False)
    org_user = models.ForeignKey(
        OrgUser, on_delete=models.CASCADE, related_name="calendar_notifications"
    )
    event = models.ForeignKey(
        CalendarEvent, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.CharField(max_length=500)
    read_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    if TYPE_CHECKING:
        org_user_id: int
        event_id: int

    class Meta:
        verbose_name = "EVT_CalendarNotification"
        ordering = ["-created"]
        indexes = [
            models.Index(
                fields=["org_user", "read_at"], name="cal_notification_inbox_idx"
            ),
        ]

    @property
    def event_uuid(self) -> UUID:
        return self.event.uuid

    def mark_read(self) -> None:
        if self.read_at is None:
            self.read_at = timezone.now()
            self.save(update_fields=["read_at"])

    def __str__(self):
        return f"CalendarNotification: {self.pk}, org_user: {self.org_user_id}"
