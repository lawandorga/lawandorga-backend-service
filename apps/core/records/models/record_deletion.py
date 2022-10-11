from django.db import models
from django.utils import timezone

from apps.core.models import UserProfile
from apps.core.records.models.record import Record


class RecordDeletion(models.Model):
    record = models.ForeignKey(
        Record, related_name="deletions", on_delete=models.SET_NULL, null=True
    )
    explanation = models.TextField()
    requested_by = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="requestedrecorddeletions",
        blank=True,
    )
    processed_by = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="processedrecorddeletions",
        null=True,
    )
    processed = models.DateTimeField(null=True, blank=True)
    STATE_CHOICES = (
        ("re", "Requested"),
        ("gr", "Granted"),
        ("de", "Declined"),
    )
    state = models.CharField(max_length=2, choices=STATE_CHOICES, default="re")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "recordDeletion: {}; state: {};".format(self.pk, self.state)

    class Meta:
        verbose_name = "RecordDeletion"
        verbose_name_plural = "RecordDeletions"
        ordering = ["-state", "-created"]

    def save(self, *args, **kwargs):
        if self.state == "gr" and self.record:
            self.processed_on = timezone.now()
            super().save(*args, **kwargs)
            self.record.delete()
        else:
            super().save(*args, **kwargs)
