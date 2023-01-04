from django.db import models, transaction
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
    requestor = models.ForeignKey(
        RlcUser,
        related_name="requested_record_deletions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    processed_by = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="processedrecorddeletions",
        null=True,
    )
    processor = models.ForeignKey(
        RlcUser,
        related_name="processed_record_deletions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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
        if self.processor:
            return self.processor.name
        return ""

    @property
    def requested_by_detail(self):
        if self.requestor:
            return self.requestor.name
        return ""

    def save(self, *args, **kwargs):
        with transaction.atomic():
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
        self.processor = by
        self.processed = timezone.now()
        self.state = "gr"

    def decline(self, by: RlcUser):
        if self.state != "re":
            raise DomainError(
                "This deletion request can not be declined, because it is not in a requested state."
            )
        self.processor = by
        self.processed = timezone.now()
        self.state = "de"
