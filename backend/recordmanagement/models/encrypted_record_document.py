import re
import unicodedata

import botocore.exceptions
from django.core.files.storage import default_storage
from rest_framework.exceptions import ParseError

from backend.static.encrypted_storage import EncryptedStorage
from backend.static.storage_folders import get_storage_folder_encrypted_record_document
from backend.static.encryption import AESEncryption
from django.db.models.signals import pre_delete
from backend.api.models import UserProfile
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
    tagged = models.ManyToManyField("RecordDocumentTag", related_name="e_tagged", blank=True)
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
        local_file = default_storage.save(self.key, file)
        local_file_path = os.path.join(settings.MEDIA_ROOT, local_file)
        EncryptedStorage.encrypt_file_and_upload_to_s3(local_file_path, record_key, self.key)
        default_storage.delete(self.key)
        default_storage.delete(self.get_file_key())

    def download(self, record_key):
        # get the key with which you can find the item on aws
        key = self.get_file_key()
        # generate a local file path on where to save the file and clean it up so nothing goes wrong
        downloaded_file_path = os.path.join(settings.MEDIA_ROOT, key)
        downloaded_file_path = ''.join([i if ord(i) < 128 else '?' for i in downloaded_file_path])
        # check if the folder path exists and if not create it so that boto3 can save the file
        folder_path = downloaded_file_path[:downloaded_file_path.rindex('/')]
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        # download and decrypt the file
        try:
            EncryptedStorage.get_s3_client().download_file(settings.SCW_S3_BUCKET_NAME, key, downloaded_file_path)
        except botocore.exceptions.ClientError:
            raise ParseError(
                'The file was not found. However, it is probably still encrypted on the server. '
                'Please send an e-mail to it@law-orga.de to have the file restored.'
            )
        AESEncryption.decrypt_file(downloaded_file_path, record_key)
        # open the file to return it and delete the files from the media folder for safety reasons
        file = default_storage.open(downloaded_file_path[:-4])

        # return a delete function so that the file can be deleted after it was used
        def delete():
            default_storage.delete(downloaded_file_path[:-4])
            default_storage.delete(downloaded_file_path)

        # return
        return file, delete

        # key = self.get_file_key()
        # downloaded_file_path = os.path.join(settings.MEDIA_ROOT, key)
        # folder_path = downloaded_file_path[:downloaded_file_path.rindex('/')]
        # if not os.path.exists(folder_path):
        #     os.makedirs(folder_path)
        # EncryptedStorage.get_s3_client().download_file(settings.SCW_S3_BUCKET_NAME, key, downloaded_file_path)
        # AESEncryption.decrypt_file(downloaded_file_path, record_key)

    def delete_on_cloud(self):
        EncryptedStorage.delete_on_s3(self.get_file_key())

    @receiver(pre_delete)
    def pre_deletion(sender, instance, **kwargs):
        if sender == EncryptedRecordDocument:
            instance.delete_on_cloud()

    def exists_on_s3(self) -> bool:
        self.exists = EncryptedStorage.file_exists(self.get_file_key())
        self.save()
        return self.exists
