from django.db import models
from django.db.models import Q

from core.auth.models import RlcUser
from core.rlc.models import Org


class EventsEvent(models.Model):
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
        ordering = ["start_time"]

    @staticmethod
    def get_all_events_for_user(rlc_user: RlcUser):
        events = EventsEvent.objects.filter(
            Q(org=rlc_user.org)
            | Q(level="GLOBAL")
            | Q(level="META", org__meta=rlc_user.org.meta)
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
        self.is_global = self.is_global if (is_global is None) else is_global
        self.name = name or self.name
        self.description = description or self.description
        self.start_time = start_time or self.start_time
        self.end_time = end_time or self.end_time

        self.save()
