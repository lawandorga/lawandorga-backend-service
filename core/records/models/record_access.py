from typing import cast

from django.db import models, transaction
from django.utils import timezone

from core.auth.models import RlcUser
from core.folders.domain.repositiories.folder import FolderRepository
from core.models import UserProfile
from core.records.models.record import Record
from core.seedwork.domain_layer import DomainError
from core.seedwork.repository import RepositoryWarehouse


class RecordAccess(models.Model):
    @classmethod
    def create(
        cls, record: Record, requestor: RlcUser, explanation=""
    ) -> "RecordAccess":
        access = RecordAccess(
            record=record, requestor=requestor, explanation=explanation
        )
        return access

    requested_by = models.ForeignKey(
        UserProfile,
        related_name="requestedrecordaccesses",
        on_delete=models.CASCADE,
        null=True,
    )
    requestor = models.ForeignKey(
        RlcUser,
        related_name="requested_record_accesses",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    processed_by = models.ForeignKey(
        UserProfile,
        related_name="processedrecordaccesses",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    processor = models.ForeignKey(
        RlcUser,
        related_name="processed_record_accesses",
        on_delete=models.SET_NULL,
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
    explanation = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "RecordAccess"
        verbose_name_plural = "RecordAccesses"
        ordering = ["-created"]

    def __str__(self):
        return "recordAccess: {};".format(self.id)

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
            if hasattr(self, "_folder"):
                r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
                r.save(self._folder)
            super().save(*args, **kwargs)

    def grant(self, by: RlcUser):
        if self.state != "re":
            raise DomainError(
                "This access request can not be granted, because it is not in a requested state."
            )

        folder = self.record.folder
        assert folder is not None
        if not folder.has_access(by):
            raise DomainError(
                "You can not give access to this record, because you have no access to this record."
            )

        folder.grant_access(self.requestor, by)  # type: ignore
        self._folder = folder

        self.state = "gr"
        self.processed_on = timezone.now()
        self.processor = by

    def decline(self, by: RlcUser):
        if self.state != "re":
            raise DomainError(
                "This access request can not be declined, because it is not in a requested state."
            )

        self.state = "de"
        self.processed_on = timezone.now()
        self.processor = by
