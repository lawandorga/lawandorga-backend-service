from django.db import models

from apps.core.models.group import Group
from apps.files.models.folder import Folder
from apps.files.models.folder_permission import FolderPermission


class PermissionForFolder(models.Model):
    permission = models.ForeignKey(
        FolderPermission,
        related_name="in_permission_for_folder",
        null=False,
        on_delete=models.CASCADE,
    )
    group_has_permission = models.ForeignKey(
        Group,
        related_name="group_has_folder_permissions",
        on_delete=models.CASCADE,
        blank=False,
        null=True,
    )
    folder = models.ForeignKey(
        Folder,
        related_name="folder_permissions_for_folder",
        null=False,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "PermissionForFolder"
        verbose_name_plural = "PermissionsForFolders"

    def __str__(self):
        return "permissionForFolder: {}; folder: {}; permission: {};".format(
            self.pk, self.folder.name, self.permission.name
        )
