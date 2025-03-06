from datetime import datetime

import bleach
from django.db import models
from django.db.models import Q

from core.auth.models import OrgUser
from core.org.models import Org
from core.seedwork.domain_layer import DomainError


class EventsEvent(models.Model):
    @classmethod
    def create(
        cls,
        org: Org,
        name: str,
        description: str,
        level: str,
        start_time: datetime,
        end_time: datetime,
    ):
        if start_time > end_time:
            raise DomainError("The start time must be before the end time.")
        clean_description = bleach.clean(
            description,
            tags=["a", "p", "strong", "em", "ul", "ol", "li", "s"],
            attributes={"a": ["href"]},
        )
        return cls(
            org=org,
            name=name,
            level=level,
            description=clean_description,
            start_time=start_time,
            end_time=end_time,
        )

    LEVEL_CHOICES = [
        ("ORG", "Organization"),
        ("META", "Meta"),
        ("GLOBAL", "Global"),
    ]

    org = models.ForeignKey(Org, related_name="events", on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_global = models.BooleanField(default=False)  # deprecated: remove after migration
    level = models.CharField(max_length=200, choices=LEVEL_CHOICES, default="ORG")
    name = models.CharField(null=False, max_length=200)
    description = models.TextField(blank=True, default="")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        verbose_name = "EVT_EventsEvent"
        verbose_name = "EVT_EventsEvents"
        ordering = ["start_time"]

    @staticmethod
    def get_all_events_for_user(org_user: OrgUser):
        events = EventsEvent.objects.filter(
            Q(org=org_user.org)
            | Q(level="GLOBAL")
            | Q(level="META", org__meta=org_user.org.meta)
        )
        return events

    def update_information(
        self,
        is_global=None,
        name=None,
        description=None,
        start_time=None,
        end_time=None,
    ):
        if start_time is not None and end_time is not None and start_time > end_time:
            raise DomainError("The start time must be before the end time.")

        clean_description = None
        if description is not None:
            clean_description = bleach.clean(
                description,
                tags=["a", "p", "strong", "em", "ul", "ol", "li", "s"],
                attributes={"a": ["href"]},
            )
        self.is_global = self.is_global if (is_global is None) else is_global
        self.name = name or self.name
        self.description = clean_description or self.description
        self.start_time = start_time or self.start_time
        self.end_time = end_time or self.end_time
