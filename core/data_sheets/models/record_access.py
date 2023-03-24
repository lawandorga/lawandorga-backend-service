from typing import cast

from django.db import models, transaction
from django.utils import timezone

from core.auth.models import RlcUser
from core.folders.domain.repositiories.folder import FolderRepository
from core.data_sheets.models.record import Record
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

    requestor = models.ForeignKey(
        RlcUser,
        related_name="requested_record_accesses",
        on_delete=models.CASCADE,
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
            if self.state == "gr" and not self.record.folder.has_access(self.requestor):
                r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
                folder = r.retrieve(self.requestor.org_id, self.record.folder_uuid)
                folder.grant_access(self.requestor, self.processor)
                r.save(folder)
            super().save(*args, **kwargs)

    def grant(self, by: RlcUser):
        if self.state != "re":
            raise DomainError(
                "This access request can not be granted, because it is not in a requested state."
            )

        if not self.record.folder.has_access(by):
            raise DomainError(
                "You can not give access to this record, because you have no access to this record."
            )

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
