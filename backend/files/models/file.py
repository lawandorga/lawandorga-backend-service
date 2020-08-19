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

from datetime import datetime

import pytz
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from backend.api.models import UserProfile
from backend.static.encrypted_storage import EncryptedStorage
from .folder import Folder


class File(models.Model):
    name = models.CharField(max_length=255)

    creator = models.ForeignKey(
        UserProfile, related_name="files_created", on_delete=models.SET_NULL, null=True
    )
    created = models.DateTimeField(auto_now_add=True)

    last_editor = models.ForeignKey(
        UserProfile,
        related_name="last_edited",
        on_delete=models.SET_NULL,
        null=True,
        default=None,
    )
    last_edited = models.DateTimeField(auto_now_add=True)

    folder = models.ForeignKey(
        Folder, related_name="files_in_folder", on_delete=models.CASCADE, null=False
    )
    size = models.BigIntegerField(null=False)

    def __str__(self):
        return "file: " + self.get_file_key()

    def get_file_key(self):
        return self.folder.get_file_key() + self.name

    def delete_on_cloud(self):
        EncryptedStorage.delete_on_s3(self.get_file_key() + ".enc")

    @receiver(pre_delete)
    def pre_deletion(sender, instance, **kwargs):
        if sender == File:
            instance.delete_on_cloud()
            instance.folder.propagate_new_size_up(-instance.size)
            # instance.folder.number_of_files -= 1
            instance.folder.save()

    @receiver(post_save)
    def post_save(sender, instance, **kwargs):
        if sender == File:
            instance.folder.propagate_new_size_up(instance.size)
            # instance.folder.number_of_files += 1
            instance.folder.save()

    def download(self, aes_key, local_destination_folder):
        EncryptedStorage.download_from_s3_and_decrypt_file(
            self.get_file_key() + ".enc", aes_key, local_destination_folder
        )
        # EncryptedStorage.download_file_from_s3(self.get_file_key(), os.path.join(local_destination_folder, self.name + '.enc'))

    @staticmethod
    def create_or_update(file):
        try:
            existing = File.objects.get(folder=file.folder, name=file.name)
            existing.last_editor = file.last_editor
            existing.last_edited = datetime.utcnow().replace(tzinfo=pytz.utc)
            existing.size = file.size
            existing.save()
            return existing
        except:
            file.save()
            return file

    @staticmethod
    def create_or_duplicate(file):
        try:
            File.objects.get(folder=file.folder, name=file.name)
        except:
            file.save()
            return file
        count = 1
        extension_index = file.name.rindex(".")
        base = file.name[:extension_index]
        extension = file.name[extension_index:]
        while True:
            new_name = base + " (" + str(count) + ")" + extension
            try:
                File.objects.get(folder=file.folder, name=new_name)
                count += 1
            except:
                file.name = new_name
                file.save()
                return file
