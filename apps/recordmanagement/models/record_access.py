from django.db import models

from apps.api.models import UserProfile
from apps.recordmanagement.models.record import Record


class RecordAccess(models.Model):
    requested_by = models.ForeignKey(
        UserProfile, related_name="requestedrecordaccesses", on_delete=models.CASCADE
    )
    processed_by = models.ForeignKey(
        UserProfile,
        related_name="processedrecordaccesses",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    record = models.ForeignKey(
        Record, related_name="e_permissions_requested", on_delete=models.CASCADE
    )
    processed_on = models.DateTimeField(null=True, blank=True)
    STATE_CHOICES = (
        ("re", "requested"),
        ("gr", "granted"),
        ("de", "declined"),
    )
    state = models.CharField(max_length=2, choices=STATE_CHOICES, default="re")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "RecordAccess"
        verbose_name_plural = "RecordAccesses"
        ordering = ["-state", "-created"]

    def __str__(self):
        return "recordAccess: {};".format(self.id)
