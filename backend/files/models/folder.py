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

from backend.api.models import Rlc, UserProfile
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
        Rlc, related_name="folders", on_delete=models.CASCADE, null=False
    )

    def __str__(self):
        return "folder: " + self.name

    def get_file_key(self):
        if self.parent:
            key = self.parent.get_file_key()
        else:
            key = get_storage_base_files_folder(self.rlc.id)
        return key + self.name + "/"

    def propagate_new_size_up(self, delta=-1):
        if self.parent:
            self.parent.propagate_new_size_up(delta)
        self.size = self.size + delta
        if delta > 0:
            self.number_of_files = self.number_of_files + 1
        else:
            self.number_of_files = self.number_of_files - 1
        self.save()

    def update_folder_tree_sizes(self, delta):
        self.size = self.size - delta
        self.propagate_new_size_up(delta)

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

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if (
            Folder.objects.filter(parent=self.parent, name=self.name, rlc=self.rlc)
            .exclude(pk=self.id)
            .count()
            > 0
        ):
            raise Exception("duplicate folder")
        super().save(force_insert, force_update, using, update_fields)

    def user_has_permission_read(self, user):
        from backend.files.models import PermissionForFolder

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
        users_groups = user.group_members.all()
        p_read = FolderPermission.objects.get(name=PERMISSION_READ_FOLDER)
        relevant_permissions = PermissionForFolder.objects.filter(
            folder__in=relevant_folders,
            group_has_permission__in=users_groups,
            permission=p_read,
        )
        if relevant_permissions.count() >= 1:
            return True

        return False

    def user_has_permission_write(self, user):
        from backend.files.models import PermissionForFolder

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
        users_groups = user.group_members.all()
        p_write = FolderPermission.objects.get(name=PERMISSION_WRITE_FOLDER)
        relevant_permissions = PermissionForFolder.objects.filter(
            folder__in=relevant_folders,
            group_has_permission__in=users_groups,
            permission=p_write,
        )
        if relevant_permissions.count() >= 1:
            return True

        return False

    def user_can_see_folder(self, user):
        from backend.files.models import PermissionForFolder

        if user.rlc != self.rlc:
            return False
        if self.user_has_permission_read(user) or self.user_has_permission_write(user):
            return True
        children = self.get_all_children()
        users_groups = user.group_members.all()
        relevant_permissions = PermissionForFolder.objects.filter(
            folder__in=children, group_has_permission__in=users_groups
        )
        if relevant_permissions.count() >= 1:
            return True
        return False

    def get_groups_permission(self, group):
        from backend.files.models import PermissionForFolder

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

    def get_all_groups_permissions(self):
        from backend.api.models import Group
        from backend.files.serializers import PermissionForFolderNestedSerializer

        groups = list(Group.objects.filter(from_rlc=self.rlc))

        allGroupsPermissions = {"SEE": [], "WRITE": [], "READ": []}
        for group in groups:
            perm_string, perm = self.get_groups_permission(group)
            if perm:
                data = PermissionForFolderNestedSerializer(perm).data
            else:
                data = {"general": True}
            if perm_string == "":
                continue
            elif perm_string == "WRITE":
                allGroupsPermissions["WRITE"].append(data)
            elif perm_string == "READ":
                allGroupsPermissions["READ"].append(data)
            elif perm_string == "SEE":
                allGroupsPermissions["SEE"].append(data)

        return allGroupsPermissions

    def get_all_groups_permissions_new(self):
        from backend.api.models import Group, HasPermission, Permission
        from backend.files.models import PermissionForFolder
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
        overall_permissions = Permission.objects.filter(
            name__in=overall_permissions_strings
        )
        has_permissions_for_groups = HasPermission.objects.filter(
            group_has_permission__in=groups,
            permission_for_rlc=self.rlc,
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

    def download_folder(self, aes_key, local_path=""):
        # create local folder
        # download all files in this folder to local folder
        # call download_folder of children
        from backend.files.models import File
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
    def get_folder_from_path(path, rlc):
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
            folder = folder.child_folders.filter(name=path_parts[i]).first()
        return folder

    @staticmethod
    def create_folders_for_file_path(root_folder, path, user):
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
