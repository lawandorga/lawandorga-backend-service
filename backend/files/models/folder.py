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
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from backend.api.models import Rlc, UserProfile
from backend.files.static.folder_permissions import PERMISSION_WRITE_FOLDER
from backend.static.permissions import PERMISSION_READ_ALL_FOLDERS_RLC, PERMISSION_WRITE_ALL_FOLDERS_RLC
from backend.static.storage_folders import get_storage_base_files_folder, get_temp_storage_folder


class Folder(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(UserProfile, related_name="folders_created", on_delete=models.SET_NULL, null=True)
    size = models.BigIntegerField(default=0)
    parent = models.ForeignKey('self', related_name="child_folders", null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now_add=True)
    number_of_files = models.BigIntegerField(default=0)
    rlc = models.ForeignKey(Rlc, related_name="folders", on_delete=models.CASCADE, null=False)

    def __str__(self):
        return 'folder: ' + self.name

    def get_file_key(self):
        if self.parent:
            key = self.parent.get_file_key()
        else:
            key = get_storage_base_files_folder(self.rlc.id)
        return key + self.name + '/'

    def delete_on_cloud(self):
        # delete folder an subfolder on storage
        # TODO: files!
        pass

    def propagate_new_size_up(self, delta=-1):
        if self.parent:
            self.parent.propagate_new_size_up(delta)
        self.size = self.size + delta
        # self.save()

    @receiver(pre_delete)
    def propagate_deletion(sender, instance, **kwargs):
        if sender == Folder:
            instance.propagate_new_size_up(-instance.size)
            instance.delete_on_cloud()

    @receiver(post_save)
    def propagate_saving(sender, instance, **kwargs):
        if sender == Folder:
            instance.propagate_new_size_up(instance.size)

    def get_all_parents(self):
        if not self.parent:
            return []
        elif self.parent.parent:
            return self.parent.get_all_parents() + [self.parent]
        else:
            return [self.parent]

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if Folder.objects.filter(parent=self.parent, name=self.name, rlc=self.rlc).exclude(pk=self.id).count() > 0:
            raise Exception('duplicate folder')
        super().save(force_insert, force_update, using, update_fields)

    def user_has_permission_read(self, user):
        from backend.files.models import PermissionForFolder
        if user.has_permission(for_rlc=user.rlc, permission=PERMISSION_READ_ALL_FOLDERS_RLC) or \
            user.has_permission(for_rlc=user.rlc, permission=PERMISSION_WRITE_ALL_FOLDERS_RLC):
            return True

        relevant_folders = self.get_all_parents() + [self]
        relevant_permissions = PermissionForFolder.objects.filter(folder__in=relevant_folders)
        if relevant_permissions.count() == 0:
            return True

        relevant_folders.reverse()
        for folder in relevant_folders:
            permissions_for_folder = PermissionForFolder.objects.filter(folder=folder)
            if permissions_for_folder.count() > 0:
                if permissions_for_folder.filter(
                    group_has_permission_id__in=user.group_members.values_list('pk', flat=True)).count() == 0:
                    return False
        return True

    def user_has_permission_write(self, user):
        from backend.files.models import PermissionForFolder
        if user.has_permission(for_rlc=user.rlc, permission=PERMISSION_WRITE_ALL_FOLDERS_RLC):
            return True

        relevant_folders = self.get_all_parents() + [self]
        relevant_permissions = PermissionForFolder.objects.filter(folder__in=relevant_folders)
        if relevant_permissions.count() == 0:
            return True

        relevant_folders.reverse()
        for folder in relevant_folders:
            permissions_for_folder = PermissionForFolder.objects.filter(folder=folder)
            if permissions_for_folder.count() > 0:
                if permissions_for_folder.filter(
                    group_has_permission_id__in=user.group_members.values_list('pk', flat=True),
                    permission__name=PERMISSION_WRITE_FOLDER).count() == 0:
                    return False
        return True

    def download_folder(self, local_path=''):
        # create local folder
        # download all files in this folder to local folder
        # call download_folder of children
        from backend.files.models import File
        import os

        files_in_folder = File.objects.filter(folder=self)
        try:
            os.makedirs(os.path.join(get_temp_storage_folder(), local_path, self.name))
        except:
            pass
        for file in files_in_folder:
            file.download(os.path.join(local_path, self.name))
        for child in self.child_folders.all():
            child.download_folder(local_path + self.name + '/')

    @staticmethod
    def get_folder_from_path(path, rlc):
        path_parts = path.split('/')
        i = 0
        folder = Folder.objects.filter(name=path_parts[i], parent=None, rlc=rlc).first()
        if not folder:
            return None
        while True:
            i += 1
            if i >= path_parts.__len__() or path_parts[i] == '':
                break
            folder = folder.child_folders.filter(name=path_parts[i]).first()
        return folder

    @staticmethod
    def create_folders_for_file_path(root_folder, path, user):
        path_parts = path.split('/')
        i = 0
        folder = root_folder
        while True:
            if i + 1 >= path_parts.__len__() or path_parts[i] == '':
                return folder
            child = folder.child_folders.filter(name=path_parts[i]).first()
            if child:
                folder = child
            else:
                break
            i += 1
        # if needed, create new folders
        new_child = Folder(name=path_parts[i], parent=folder, creator=user, rlc=user.rlc)
        new_child.save()
        folder = new_child
        i += 1
        while True:
            if i + 1 >= path_parts.__len__() or path_parts[i] == '':
                return folder
            new_child = Folder(name=path_parts[i], parent=folder, creator=user, rlc=user.rlc)
            new_child.save()
            folder = new_child
            i += 1
