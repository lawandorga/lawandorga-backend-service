from typing import TYPE_CHECKING, Optional
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
    enc_parent_key = models.JSONField(null=True, blank=True)
    keys = models.JSONField(blank=True)
    group_keys = models.JSONField(blank=True, null=True)
    items = models.JSONField(blank=True)
    stop_inherit = models.BooleanField(default=False)
    restricted = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    if TYPE_CHECKING:
        org_id: int
        _parent_id: int | None

    class Meta:
        verbose_name = "FoldersFolder"
        verbose_name_plural = "FoldersFolders"
        ordering = ["name"]

    def __str__(self):
        return "foldersFolder: {};".format(self.pk)

    @property
    def parent(self) -> Optional[UUID]:
        if self._parent_id is None:
            return None
        return self._parent_id

    @staticmethod
    def query() -> QuerySet:
        return FoldersFolder.objects.select_related("_parent")
