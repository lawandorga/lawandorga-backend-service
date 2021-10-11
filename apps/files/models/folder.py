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
from apps.api.models import UserProfile
from apps.api.models.rlc import Rlc
from apps.files.models.folder_permission import FolderPermission
from apps.files.static.folder_permissions import (
    PERMISSION_READ_FOLDER,
    PERMISSION_WRITE_FOLDER,
)
from apps.static.permissions import (
    PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC,
    PERMISSION_READ_ALL_FOLDERS_RLC,
    PERMISSION_WRITE_ALL_FOLDERS_RLC,
)
from apps.static.storage_folders import get_storage_base_files_folder


class Folder(models.Model):
    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey("self", related_name="child_folders", null=True, on_delete=models.CASCADE, blank=True)
    rlc = models.ForeignKey(Rlc, related_name="folders", on_delete=models.CASCADE, null=False, blank=True)

    class Meta:
        verbose_name = "Folder"
        verbose_name_plural = "Folders"

    def __str__(self) -> str:
        return "folder: {}; name: {};".format(self.pk, self.name)

    def get_file_key(self) -> str:
        if self.parent:
            key = self.parent.get_file_key()
        else:
            key = get_storage_base_files_folder(self.rlc.id)
        return key + self.name + "/"

    def get_all_parents(self):
        if not self.parent:
            return []
        elif self.parent.parent:
            return self.parent.get_all_parents() + [self.parent]
        else:
            return [self.parent]

    def get_all_children(self):
        if not self.child_folders:
            return []
        children = []
        for child in self.child_folders.all():
            children.append(child)
            children += child.get_all_children()
        return children

    def user_has_permission_read(self, user: UserProfile) -> bool:

        if user.rlc != self.rlc:
            return False
        if (
            user.has_permission(
                for_rlc=user.rlc, permission=PERMISSION_READ_ALL_FOLDERS_RLC
            )
            or user.has_permission(
            for_rlc=user.rlc, permission=PERMISSION_WRITE_ALL_FOLDERS_RLC
        )
            or user.has_permission(
            for_rlc=user.rlc, permission=PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC
        )
        ):
            return True

        relevant_folders = self.get_all_parents() + [self]
        users_groups = user.rlcgroups.all()
        p_read = FolderPermission.objects.get(name=PERMISSION_READ_FOLDER)
        from apps.files.models.permission_for_folder import PermissionForFolder

        relevant_permissions = PermissionForFolder.objects.filter(
            folder__in=relevant_folders,
            group_has_permission__in=users_groups,
            permission=p_read,
        )
        if relevant_permissions.count() >= 1:
            return True

        return False

    def user_has_permission_write(self, user: UserProfile) -> bool:

        if user.rlc != self.rlc:
            return False

        # TODO: manage_folder_permissions here too? -> is for writing?
        if user.has_permission(
            for_rlc=user.rlc, permission=PERMISSION_WRITE_ALL_FOLDERS_RLC
        ) or user.has_permission(
            for_rlc=user.rlc, permission=PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC
        ):
            return True

        relevant_folders = self.get_all_parents() + [self]
        users_groups = user.rlcgroups.all()
        p_write = FolderPermission.objects.get(name=PERMISSION_WRITE_FOLDER)
        from apps.files.models.permission_for_folder import PermissionForFolder

        relevant_permissions = PermissionForFolder.objects.filter(
            folder__in=relevant_folders,
            group_has_permission__in=users_groups,
            permission=p_write,
        )
        if relevant_permissions.count() >= 1:
            return True

        return False

    def user_can_see_folder(self, user: UserProfile) -> bool:
        from apps.files.models.permission_for_folder import PermissionForFolder

        if user.rlc != self.rlc:
            return False
        if self.user_has_permission_read(user) or self.user_has_permission_write(user):
            return True
        children = self.get_all_children()
        users_groups = user.rlcgroups.all()
        if PermissionForFolder.objects.filter(folder__in=children, group_has_permission__in=users_groups).exists():
            return True
        return False
