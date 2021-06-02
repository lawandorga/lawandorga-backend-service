#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2020  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>

from django.db import models

from backend.api.models.group import Group
from backend.files.models.folder import Folder
from backend.files.models.folder_permission import FolderPermission


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

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if (
            PermissionForFolder.objects.filter(
                permission=self.permission,
                folder=self.folder,
                group_has_permission=self.group_has_permission,
            ).count()
            > 0
        ):
            if self.id:
                self.delete()
            else:
                return
            raise Exception("PermissionForFolder doubled, deleting")
        super().save(force_insert, force_update, using, update_fields)
