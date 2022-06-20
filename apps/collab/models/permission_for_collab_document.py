from django.db import models

from apps.api.models import Group
from apps.collab.models import CollabDocument, CollabPermission


class PermissionForCollabDocument(models.Model):
    permission = models.ForeignKey(
        CollabPermission,
        related_name="in_permission_for_document",
        null=False,
        on_delete=models.CASCADE,
    )
    group_has_permission = models.ForeignKey(
        Group,
        related_name="group_has_collab_permission",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    document = models.ForeignKey(
        CollabDocument,
        related_name="collab_permissions",
        on_delete=models.CASCADE,
        null=False,
    )

    class Meta:
        unique_together = ["permission", "group_has_permission", "document"]
