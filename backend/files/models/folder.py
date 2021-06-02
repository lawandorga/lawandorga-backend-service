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
from backend.api.models import UserProfile
from backend.api.models.rlc import Rlc
from backend.files.models.folder_permission import FolderPermission
from backend.files.static.folder_permissions import (
    PERMISSION_READ_FOLDER,
    PERMISSION_WRITE_FOLDER,
)
from backend.static.permissions import (
    PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC,
    PERMISSION_READ_ALL_FOLDERS_RLC,
    PERMISSION_WRITE_ALL_FOLDERS_RLC,
)
from backend.static.storage_folders import (
    get_storage_base_files_folder,
    get_temp_storage_folder,
)
from backend.static.error_codes import ERROR__FILES__FOLDER_NOT_EXISTING
from backend.api.errors import CustomError
from backend.static.logger import Logger


class Folder(models.Model):
    name = models.CharField(max_length=255)

    creator = models.ForeignKey(
        UserProfile,
        related_name="folders_created",
        on_delete=models.SET_NULL,
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)

    last_editor = models.ForeignKey(
        UserProfile,
        related_name="last_edited_folders",
        on_delete=models.SET_NULL,
        null=True,
    )
    last_edited = models.DateTimeField(auto_now_add=True)

    size = models.BigIntegerField(default=0)
    parent = models.ForeignKey(
        "self", related_name="child_folders", null=True, on_delete=models.CASCADE
    )
    number_of_files = models.BigIntegerField(default=0)
    rlc = models.ForeignKey(
        Rlc, related_name="folders", on_delete=models.CASCADE, null=False, blank=True
    )

    class Meta:
        verbose_name = "Folder"
        verbose_name_plural = "Folders"

    def __str__(self) -> str:
        return "folder: ; name: {};".format(self.pk, self.name)

    def get_file_key(self) -> str:
        if self.parent:
            key = self.parent.get_file_key()
        else:
            key = get_storage_base_files_folder(self.rlc.id)
        return key + self.name + "/"

    def propagate_new_size_up(self, delta: int = -1) -> None:
        if self.parent:
            self.parent.propagate_new_size_up(delta)
        self.size = self.size + delta
        if delta > 0:
            self.number_of_files = self.number_of_files + 1
        else:
            self.number_of_files = self.number_of_files - 1
        self.save()

    def update_folder_tree_sizes(self, delta: int) -> None:
        self.size = self.size - delta
        self.propagate_new_size_up(delta)

    def get_all_parents(self) -> ["Folder"]:
        if not self.parent:
            return []
        elif self.parent.parent:
            return self.parent.get_all_parents() + [self.parent]
        else:
            return [self.parent]

    def get_all_children(self) -> ["Folder"]:
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
        from backend.files.models.permission_for_folder import PermissionForFolder

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
        from backend.files.models.permission_for_folder import PermissionForFolder

        relevant_permissions = PermissionForFolder.objects.filter(
            folder__in=relevant_folders,
            group_has_permission__in=users_groups,
            permission=p_write,
        )
        if relevant_permissions.count() >= 1:
            return True

        return False

    def user_can_see_folder(self, user: UserProfile) -> bool:
        from backend.files.models.permission_for_folder import PermissionForFolder

        if user.rlc != self.rlc:
            return False
        if self.user_has_permission_read(user) or self.user_has_permission_write(user):
            return True
        children = self.get_all_children()
        users_groups = user.rlcgroups.all()
        if PermissionForFolder.objects.filter(folder__in=children, group_has_permission__in=users_groups).exists():
            return True
        return False

    def get_groups_permission(self, group) -> {}:

        from backend.files.models.permission_for_folder import PermissionForFolder

        if group.has_group_permission(PERMISSION_WRITE_ALL_FOLDERS_RLC):
            return "WRITE", None
        elif group.has_group_permission(
            PERMISSION_READ_ALL_FOLDERS_RLC
        ) or group.has_group_permission(PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC):
            return "READ", None

        parent_folders = self.get_all_parents()
        p_write = FolderPermission.objects.get(name=PERMISSION_WRITE_FOLDER)
        relevant_permissions = PermissionForFolder.objects.filter(
            folder__in=parent_folders, group_has_permission=group, permission=p_write
        )
        if relevant_permissions.count() >= 1:
            return "WRITE", relevant_permissions.first()

        relevant_permissions = PermissionForFolder.objects.filter(
            folder=self, group_has_permission=group, permission=p_write
        )
        if relevant_permissions.count() > 0:
            return "WRITE", relevant_permissions.first()

        p_read = FolderPermission.objects.get(name=PERMISSION_READ_FOLDER)
        relevant_permissions = PermissionForFolder.objects.filter(
            folder__in=parent_folders, group_has_permission=group, permission=p_read
        )
        if relevant_permissions.count() >= 1:
            return "READ", relevant_permissions.first()
        relevant_permissions = PermissionForFolder.objects.filter(
            folder=self, group_has_permission=group, permission=p_read
        )
        if relevant_permissions.count() > 0:
            return "READ", relevant_permissions.first()

        children = self.get_all_children()
        relevant_permissions = PermissionForFolder.objects.filter(
            folder__in=children, group_has_permission=group
        )
        if relevant_permissions.count() >= 1:
            return "SEE", relevant_permissions.first()
        return "", None

    def get_all_groups_permissions(
        self,
    ) -> (["PermissionForFolder"], ["PermissionForFolder"], ["HasPermission"]):
        from backend.api.models.group import Group
        from backend.files.models.permission_for_folder import PermissionForFolder
        from backend.static.permissions import (
            PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC,
            PERMISSION_READ_ALL_FOLDERS_RLC,
            PERMISSION_WRITE_ALL_FOLDERS_RLC,
        )

        groups = list(Group.objects.filter(from_rlc=self.rlc))

        folder_permissions = []
        folder_visible = []

        overall_permissions_strings = [
            PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC,
            PERMISSION_READ_ALL_FOLDERS_RLC,
            PERMISSION_WRITE_ALL_FOLDERS_RLC,
        ]
        from backend.api.models.permission import Permission

        overall_permissions = Permission.objects.filter(
            name__in=overall_permissions_strings
        )
        from backend.api.models.has_permission import HasPermission

        has_permissions_for_groups = HasPermission.objects.filter(
            group_has_permission__in=groups,
            permission__in=overall_permissions,
        )

        parents = self.get_all_parents() + [self]
        children = self.get_all_children()
        for group in groups:
            from_parents = list(
                PermissionForFolder.objects.filter(
                    folder__in=parents, group_has_permission=group
                )
            )
            folder_permissions.extend(from_parents)
            from_children = list(
                PermissionForFolder.objects.filter(
                    folder__in=children, group_has_permission=group
                )
            )
            folder_visible.extend(from_children)

        return folder_permissions, folder_visible, list(has_permissions_for_groups)

    def download_folder(self, aes_key: str, local_path: str = "") -> None:
        # create local folder
        # download all files in this folder to local folder
        # call download_folder of children
        from backend.files.models.file import File
        import os

        files_in_folder = File.objects.filter(folder=self)
        try:
            if local_path == "":
                local_path = get_temp_storage_folder()
            os.makedirs(os.path.join(local_path, self.name))
        except:
            pass
        for file in files_in_folder:
            file.download(aes_key, os.path.join(local_path, self.name))
        for child in self.child_folders.all():
            child.download_folder(aes_key, os.path.join(local_path, self.name))

    @staticmethod
    def get_folder_from_path(path: str, rlc: Rlc) -> "Folder":
        path_parts = path.split("/")
        i = 0
        folder = Folder.objects.filter(name=path_parts[i], parent=None, rlc=rlc).first()
        if not folder:
            if path_parts[0] == "files":
                folder = Folder(rlc=rlc, name=path_parts[i])
                folder.save()
                return folder
            return None
        while True:
            i += 1
            if i >= path_parts.__len__() or path_parts[i] == "":
                break
            if not folder:
                Logger.error(
                    "folder " + path + " does not exist for rlc " + str(rlc.name)
                )
                raise CustomError(ERROR__FILES__FOLDER_NOT_EXISTING)
            folder = folder.child_folders.filter(name=path_parts[i]).first()
        return folder

    @staticmethod
    def create_folders_for_file_path(
        root_folder: "Folder", path: str, user: UserProfile
    ) -> "Folder":
        """
        creates folder for path, returns last folder created/in path
        :param root_folder:
        :param path:
        :param user:
        :return: returns last folder in path
        """
        path_parts = path.split("/")
        i = 0
        folder = root_folder
        while True:
            if i + 1 >= path_parts.__len__() or path_parts[i] == "":
                return folder
            child = folder.child_folders.filter(name=path_parts[i]).first()
            if child:
                folder = child
            else:
                break
            i += 1
        # if needed, create new folders
        new_child = Folder(
            name=path_parts[i],
            parent=folder,
            creator=user,
            rlc=user.rlc,
            last_editor=user,
        )
        new_child.save()
        folder = new_child
        i += 1
        while True:
            if i + 1 >= path_parts.__len__() or path_parts[i] == "":
                return folder
            new_child = Folder(
                name=path_parts[i],
                parent=folder,
                creator=user,
                rlc=user.rlc,
                last_editor=user,
            )
            new_child.save()
            folder = new_child
            i += 1
