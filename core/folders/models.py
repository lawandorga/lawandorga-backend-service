from typing import TYPE_CHECKING
from uuid import uuid4

from django.db import models
from django.db.models import QuerySet

from core.rlc.models import Org


class FOL_Folder(models.Model):
    _parent = models.ForeignKey(
        "FOL_Folder", on_delete=models.CASCADE, null=True, blank=True
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
        verbose_name = "FOL_Folder"
        verbose_name_plural = "FOL_Folders"
        ordering = ["name"]

    def __str__(self):
        return "folder: {};".format(self.pk)

    @staticmethod
    def query() -> QuerySet:
        return FOL_Folder.objects.select_related("_parent")


class FOL_ClosureTable(models.Model):
    parent = models.ForeignKey(
        FOL_Folder,
        related_name="children_connections",
        on_delete=models.CASCADE,
        db_index=True,
    )
    child = models.ForeignKey(
        FOL_Folder,
        related_name="parent_connections",
        on_delete=models.CASCADE,
        db_index=True,
    )

    class Meta:
        verbose_name = "FOL_ClosureTable"
        verbose_name_plural = "FOL_ClosureTable"
        unique_together = ("parent", "child")
        ordering = ["parent", "child"]

    def __str__(self):
        return "parent: {}; child: {};".format(self.parent, self.child)
