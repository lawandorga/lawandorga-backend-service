from typing import Optional
from uuid import uuid4

from django.db import models

from core.auth.models import RlcUser


class RecordsView(models.Model):
    @classmethod
    def create(cls, name: str, user: RlcUser, columns=list[str], pk=0) -> "RecordsView":
        record = RecordsView(name=name, columns=columns, user=user)
        if pk:
            record.pk = pk
        return record

    name = models.CharField(max_length=200)
    user = models.ForeignKey(
        RlcUser, related_name="records_views", on_delete=models.CASCADE
    )
    columns = models.JSONField()
    uuid = models.UUIDField(db_index=True, unique=True, default=uuid4)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "RecordsView"
        verbose_name_plural = "RecordsViews"

    def __str__(self):
        return "recordsView: {}; user: {};".format(self.uuid, self.user.email)

    def update_information(self, name: Optional[str], columns: Optional[list[str]]):
        if name is not None:
            self.name = name
        if columns is not None:
            self.columns = columns
