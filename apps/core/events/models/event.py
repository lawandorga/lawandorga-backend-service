from typing import List

from django.db import models

from apps.core.auth.models import RlcUser
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
        raw_events: List[Event] = list(Event.objects.filter(org=rlc_user.org))  # TODO: Return global events
        all_events = []
        for e in raw_events:
            d = {
                "id": e.id,
                "created": e.created,
                "updated": e.updated,
                "is_global": e.is_global,
                "name": e.name,
                "description": e.description,
                "start_time": e.start_time,
                "end_time": e.end_time
            }
            all_events.append(d)
        return all_events
