import uuid

from django.db import models
from django.utils import timezone

from core.auth.models import RlcUser
from core.records.models.record import RecordsRecord
from core.seedwork.domain_layer import DomainError


class RecordsAccessRequest(models.Model):
    @classmethod
    def create(
        cls, record: RecordsRecord, requestor: RlcUser, explanation=""
    ) -> "RecordsAccessRequest":
        access = RecordsAccessRequest(
            record=record, requestor=requestor, explanation=explanation
        )
        return access

    uuid = models.UUIDField(unique=True, db_index=True, default=uuid.uuid4)
    requestor = models.ForeignKey(
        RlcUser,
        related_name="records_requested_access_requests",
        on_delete=models.CASCADE,
    )
    processor = models.ForeignKey(
        RlcUser,
        related_name="records_processed_access_requests",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    record = models.ForeignKey(
        RecordsRecord, related_name="access_requests", on_delete=models.CASCADE
    )
    processed_on = models.DateTimeField(null=True, blank=True)
    STATE_CHOICES = (
        ("re", "requested"),
        ("gr", "granted"),
        ("de", "declined"),
    )
    state = models.CharField(max_length=2, choices=STATE_CHOICES, default="re")
    explanation = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "RecordsAccessRequest"
        verbose_name_plural = "RecordsAccessRequestes"
        ordering = ["-created"]

    def __str__(self):
        return "RecordsAccessRequest: {};".format(self.id)

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

    def grant(self, by: RlcUser):
        if self.state != "re":
            raise DomainError(
                "This access request can not be granted, because "
                "it is not in a requested state."
            )

        if not self.record.folder.has_access(by):
            raise DomainError(
                "You can not give access to this record, because you "
                "have no access to this record."
            )

        self.state = "gr"
        self.processed_on = timezone.now()
        self.processor = by

    def decline(self, by: RlcUser):
        if self.state != "re":
            raise DomainError(
                "This access request can not be declined, because it "
                "is not in a requested state."
            )

        self.state = "de"
        self.processed_on = timezone.now()
        self.processor = by
