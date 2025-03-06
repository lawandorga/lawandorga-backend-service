import uuid

from django.db import models
from django.utils import timezone

from core.auth.models import OrgUser
from core.seedwork.domain_layer import DomainError

from .record import RecordsRecord


class RecordsDeletion(models.Model):
    @classmethod
    def create(cls, record: RecordsRecord, user: OrgUser, explanation=""):
        deletion = RecordsDeletion(
            requestor=user, record=record, explanation=explanation
        )
        return deletion

    record = models.ForeignKey(
        RecordsRecord, related_name="deletions", on_delete=models.SET_NULL, null=True
    )
    uuid = models.UUIDField(unique=True, db_index=True, default=uuid.uuid4)
    explanation = models.TextField(blank=True)
    requestor = models.ForeignKey(
        OrgUser,
        related_name="records_requested_deletions",
        on_delete=models.CASCADE,
    )
    processor = models.ForeignKey(
        OrgUser,
        related_name="records_processed_deletions",
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
        return "recordsDeletion: {}; state: {};".format(self.pk, self.state)

    class Meta:
        verbose_name = "REC_RecordDeletion"
        verbose_name_plural = "REC_RecordDeletions"
        ordering = ["-created"]

    @property
    def record_detail(self):
        if self.record:
            return self.record.token
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

    def accept(self, by: OrgUser):
        if self.state != "re":
            raise DomainError(
                "This deletion request can not be accepted, because it is not in a requested state."
            )
        self.processor = by
        self.processed = timezone.now()
        self.state = "gr"

    def decline(self, by: OrgUser):
        if self.state != "re":
            raise DomainError(
                "This deletion request can not be declined, because it is not in a requested state."
            )
        self.processor = by
        self.processed = timezone.now()
        self.state = "de"
