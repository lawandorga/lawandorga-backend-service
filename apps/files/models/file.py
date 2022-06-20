import mimetypes

from django.core.files import File as DjangoFile
from django.db import models
from django.utils import timezone

from apps.api.models.user import UserProfile
from apps.static.encryption import AESEncryption

from .folder import Folder


class File(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(
        UserProfile, related_name="files_created", on_delete=models.SET_NULL, null=True
    )
    created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)
    folder = models.ForeignKey(
        Folder, related_name="files_in_folder", on_delete=models.CASCADE
    )
    key = models.CharField(null=True, max_length=1000, unique=True)
    file = models.FileField(upload_to="files/file/", blank=True, null=True)
    exists = models.BooleanField(default=True)

    class Meta:
        verbose_name = "File"
        verbose_name_plural = "Files"
        ordering = ["exists", "-created"]

    def __str__(self):
        return "file: {}; fileKey: {};".format(self.pk, self.get_file_key())

    @property
    def mimetype(self):
        mimetype = mimetypes.guess_type(self.file.name.replace(".enc", ""))[0]
        return mimetype

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for parent in self.get_parents():
            parent.last_edited = timezone.now()
            parent.save()

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)

    def get_parents(self):
        return self.folder.get_all_parents() + [self.folder]

    def get_file_key(self):
        return self.key

    def get_encrypted_file_key(self):
        return self.get_file_key() + ".enc"

    @staticmethod
    def encrypt_file(file, aes_key_rlc=None):
        if aes_key_rlc:
            key = aes_key_rlc
        else:
            raise ValueError("You need to pass (aes_key_rlc).")
        name = file.name
        file = AESEncryption.encrypt_in_memory_file(file, key)
        file = DjangoFile(file, name="{}.enc".format(name))
        return file

    def decrypt_file(self, aes_key_rlc=None):
        if aes_key_rlc:
            key = aes_key_rlc
        else:
            raise ValueError("You need to pass (aes_key_rlc).")
        file = AESEncryption.decrypt_bytes_file(self.file, key)
        file.seek(0)
        return file
