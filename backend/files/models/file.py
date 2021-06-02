from backend.static.encrypted_storage import EncryptedStorage
from django.db.models.signals import pre_delete
from backend.api.models.user import UserProfile
from ...static.encryption import AESEncryption
from django.dispatch import receiver
from django.conf import settings
from django.db import models
from .folder import Folder
import unicodedata
import re
import os


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

    def slugify(self, unique=None):
        key = '{}{}'.format(self.folder.get_file_key(), self.name)
        if unique is not None:
            key = '{}{}_{}'.format(self.folder.get_file_key(), unique, self.name)
        special_char_map = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('ß'): 'ss', ord('Ä'): 'AE',
                            ord('Ö'): 'OE', ord('Ü'): 'UE'}
        key = key.translate(special_char_map)
        unicodedata.normalize('NFKC', key).encode('ascii', 'ignore').decode('ascii')
        key = re.sub(r'[^/.\w\s-]', '', key.lower()).strip()
        key = re.sub(r'[-\s]+', '-', key)
        if not File.objects.filter(key=key).exists():
            return key
        else:
            unique = 1 if unique is None else unique + 1
            return self.slugify(unique=unique)

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
            instance.folder.save()

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
