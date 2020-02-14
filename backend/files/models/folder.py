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
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from backend.api.models import UserProfile, Rlc
from backend.static.storage_folders import get_storage_base_files_folder


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

    @receiver(pre_delete)
    def propagate_deletion(sender, instance, **kwargs):
        if sender == Folder:
            instance.propagate_new_size_up(-instance.size)
            instance.delete_on_cloud()

    @receiver(post_save)
    def propagate_saving(sender, instance, **kwargs):
        if sender == Folder:
            instance.propagate_new_size_up(instance.size)
