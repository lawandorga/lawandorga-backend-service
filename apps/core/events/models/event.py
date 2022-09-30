from typing import List

from django.db import models

from apps.core.auth.models import RlcUser
from apps.core.events.types.schemas import EventUpdate
from apps.core.rlc.models import Org


class Event(models.Model):
    org = models.ForeignKey(Org, related_name="events", on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_global = models.BooleanField(default=False)  # level
    name = models.CharField(null=False, max_length=200)
    description = models.TextField(blank=True, default="")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    @staticmethod
    def get_all_events_for_user(rlc_user: RlcUser):
        raw_events: List[Event] = list(
            Event.objects.filter(org=rlc_user.org)
            | Event.objects.filter(is_global=True)
        )
        return raw_events

    def update_information(self, update_info: EventUpdate):
        self.is_global = update_info.is_global or self.is_global
        self.name = update_info.name or self.name
        self.description = update_info.description or self.description
        self.start_time = update_info.start_time or self.start_time
        self.end_time = update_info.end_time or self.end_time

        self.save()
