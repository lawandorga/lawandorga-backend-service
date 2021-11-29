import re
import unicodedata

import botocore.exceptions
from django.core.files.storage import default_storage
from rest_framework.exceptions import ParseError

from apps.static.encrypted_storage import EncryptedStorage
from apps.static.storage_folders import get_storage_folder_encrypted_record_document
from apps.static.encryption import AESEncryption
from django.db.models.signals import pre_delete
from apps.api.models import UserProfile
from django.dispatch import receiver
from django.conf import settings
from django.db import models
import os


class EncryptedRecordDocument(models.Model):
    name = models.CharField(max_length=200)
    creator = models.ForeignKey(
        UserProfile,
        related_name="e_record_documents_created",
        on_delete=models.SET_NULL,
        null=True,
    )
    record = models.ForeignKey("EncryptedRecord", related_name="e_record_documents", on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now_add=True)
    file_size = models.BigIntegerField(null=True)
    key = models.SlugField(null=True, allow_unicode=True, max_length=1000, unique=True)
    exists = models.BooleanField(default=True)

    class Meta:
        verbose_name = "RecordDocument"
        verbose_name_plural = "RecordDocuments"

    def __str__(self):
        return "recordDocument: {}; name: {}; creator: {}; record: {};".format(
            self.pk, self.name, self.creator.email, self.record.record_token
        )

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.key = self.slugify()
        super().save(*args, **kwargs)

    def slugify(self, unique=''):
        key = 'rlcs/{}/encrypted_records/{}/{}_{}'.format(self.record.from_rlc.pk, self.record.id, unique, self.name)
        special_char_map = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('ß'): 'ss', ord('Ä'): 'AE',
                            ord('Ö'): 'OE', ord('Ü'): 'UE'}
        key = key.translate(special_char_map)
        unicodedata.normalize('NFKC', key).encode('ascii', 'ignore').decode('ascii')
        key = re.sub(r'[^/.\w\s-]', '', key.lower()).strip()
        key = re.sub(r'[-\s]+', '-', key)
        if not EncryptedRecordDocument.objects.filter(key=key).exists():
            return key
        else:
            unique = 1 if unique == '' else int(unique) + 1
            return self.slugify(unique=unique)

    def get_key(self):
        if not self.key:
            self.key = '{}{}'.format(
                get_storage_folder_encrypted_record_document(self.record.from_rlc.pk, self.record.id),
                self.name
            )
            self.save()
        return self.key

    def get_file_key(self):
        return '{}.enc'.format(self.get_key())

    def upload(self, file, record_key):
        file = AESEncryption.encrypt_in_memory_file(file, record_key)
        key = self.get_file_key()
        default_storage.save(key, file)

    def download(self, record_key):
        key = self.get_file_key()
        return EncryptedStorage.download_encrypted_file(key, record_key)

    def delete_on_cloud(self):
        key = self.get_file_key()
        default_storage.delete(key)

    def exists_on_s3(self):
        key = self.get_file_key()
        return default_storage.exists(key)
