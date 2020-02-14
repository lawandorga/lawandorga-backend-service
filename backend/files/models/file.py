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
from backend.api.models import UserProfile
from .folder import Folder


class File(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(UserProfile, related_name="files_created", on_delete=models.SET_NULL, null=True)

    created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now_add=True)

    folder = models.ForeignKey(Folder, related_name="files_in_folder", on_delete=models.CASCADE, null=False)
    size = models.BigIntegerField(null=False)

    def get_file_key(self):
        return self.folder.get_file_key() + self.name

    def delete_on_cloud(self):
        # TODO: files!
        pass

    @receiver(pre_delete)
    def pre_deletion(sender, instance, **kwargs):
        if sender == File:
            instance.delete_on_cloud()
            instance.folder.propagate_new_size_up(-instance.size)

    @receiver(post_save)
    def post_save(sender, instance, **kwargs):
        if sender == File:
            instance.folder.propagate_new_size_up(instance.size)
