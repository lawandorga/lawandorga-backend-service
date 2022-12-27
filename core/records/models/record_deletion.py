from django.db import models
from django.utils import timezone

from core.auth.models import RlcUser
from core.models import UserProfile
from core.records.models.record import Record
from core.seedwork.domain_layer import DomainError


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
        ordering = ["-created"]

    @property
    def record_detail(self):
        if self.record:
            return self.record.name
        return "Deleted"

    @property
    def processed_by_detail(self):
        if self.processed_by:
            return self.processed_by.name
        return ""

    @property
    def requested_by_detail(self):
        if self.requested_by:
            return self.requested_by.name
        return ""

    def save(self, *args, **kwargs):
        if self.state == "gr" and self.record:
            super().save(*args, **kwargs)
            self.record.delete()
        else:
            super().save(*args, **kwargs)

    def accept(self, by: RlcUser):
        if self.state != "re":
            raise DomainError(
                "This deletion request can not be accepted, because it is not in a requested state."
            )
        self.processed_by = by.user
        self.processed = timezone.now()
        self.state = "gr"

    def decline(self, by: RlcUser):
        if self.state != "re":
            raise DomainError(
                "This deletion request can not be declined, because it is not in a requested state."
            )
        self.processed_by = by.user
        self.processed = timezone.now()
        self.state = "de"
