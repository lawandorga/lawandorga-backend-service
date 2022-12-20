from typing import Optional
from uuid import UUID, uuid4

from django.db import models
from django.db.models import QuerySet

from core.rlc.models import Org


class FoldersFolder(models.Model):
    _parent = models.ForeignKey(
        "FoldersFolder", on_delete=models.CASCADE, null=True, blank=True
    )
    uuid = models.UUIDField(default=uuid4, unique=True, db_index=True)
    name = models.CharField(max_length=1000)
    org = models.ForeignKey(
        Org, related_name="folders_folders", on_delete=models.CASCADE
    )
    keys = models.JSONField(blank=True)
    items = models.JSONField(blank=True)
    stop_inherit = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "FoldersFolder"
        verbose_name_plural = "FoldersFolders"
        ordering = ["name"]

    def __str__(self):
        return "foldersFolder: {};".format(self.pk)

    @property
    def parent(self) -> Optional[UUID]:
        if self._parent is None:
            return None
        return self._parent.uuid

    @staticmethod
    def query() -> QuerySet:
        return FoldersFolder.objects.select_related("_parent")
