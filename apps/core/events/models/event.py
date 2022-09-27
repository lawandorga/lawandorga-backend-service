from django.db import models
from apps.core.rlc.models import Org


class Event(models.Model):
    org = models.ForeignKey(Org, related_name="users", on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_global = models.BooleanField(default=False)  # level
    name = models.CharField(null=False, max_length=200)
    description = models.TextField(blank=True, default="")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
