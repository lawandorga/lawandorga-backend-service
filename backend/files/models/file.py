import os

from django.conf import settings

from backend.static.encrypted_storage import EncryptedStorage
from django.db.models.signals import post_save, pre_delete
from backend.api.models.user import UserProfile
from django.dispatch import receiver
from django.db import models
from datetime import datetime
from .folder import Folder
import unicodedata
import pytz
import re

from ...static.encryption import AESEncryption


class File(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(UserProfile, related_name="files_created", on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_editor = models.ForeignKey(
        UserProfile,
        related_name="last_edited",
        on_delete=models.SET_NULL,
        null=True,
        default=None,
    )
    last_edited = models.DateTimeField(auto_now_add=True)
    folder = models.ForeignKey(Folder, related_name="files_in_folder", on_delete=models.CASCADE)
    size = models.BigIntegerField(null=True)
    key = models.SlugField(null=True, allow_unicode=True, max_length=200, unique=True)

    class Meta:
        verbose_name = "File"
        verbose_name_plural = "Files"

    def __str__(self):
        return "file: {}; fileKey: {};".format(self.pk, self.get_file_key())

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.key = self.slugify()
        super().save(*args, **kwargs)

    def slugify(self):
        key = '{}{}'.format(self.folder.get_file_key(), self.name)
        special_char_map = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('ß'): 'ss', ord('Ä'): 'AE',
                            ord('Ö'): 'OE', ord('Ü'): 'UE'}
        key = key.translate(special_char_map)
        unicodedata.normalize('NFKC', key).encode('ascii', 'ignore').decode('ascii')
        key = re.sub(r'[^/.\w\s-]', '', key.lower()).strip()
        return re.sub(r'[-\s]+', '-', key)

    def get_file_key(self) -> str:
        return self.key

    def get_encrypted_file_key(self) -> str:
        return self.get_file_key() + ".enc"

    def delete_on_cloud(self) -> None:
        EncryptedStorage.delete_on_s3(self.get_encrypted_file_key())

    @receiver(pre_delete)
    def pre_deletion(sender, instance, **kwargs) -> None:
        if sender == File:
            instance.delete_on_cloud()
            # instance.folder.propagate_new_size_up(-instance.size)
            instance.folder.save()

    @receiver(post_save)
    def post_save(sender, instance, **kwargs) -> None:
        pass
        # if sender == File:
        #     instance.folder.propagate_new_size_up(instance.size)
        #     instance.folder.save()

    def download(self, aes_key: str):
        key = self.get_encrypted_file_key()
        downloaded_file_path = os.path.join(settings.MEDIA_ROOT, key)
        folder_path = downloaded_file_path[:downloaded_file_path.rindex('/')]
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        EncryptedStorage.get_s3_client().download_file(settings.SCW_S3_BUCKET_NAME, key, downloaded_file_path)
        AESEncryption.decrypt_file(downloaded_file_path, aes_key)

    def exists_on_s3(self) -> bool:
        return EncryptedStorage.file_exists(self.get_encrypted_file_key())

    @staticmethod
    def create_or_update(file: "File") -> "File":
        """
        creates file, or if file with name in parent folder is already existing updates
        :param file:
        :return:
        """
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
    def create_or_duplicate(file: "File") -> "File":
        """
        created file, check if file with same name already existing, if yes, create "file(x)"
        :param file:
        :return:
        """
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
