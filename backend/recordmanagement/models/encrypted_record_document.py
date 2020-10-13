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
from django_prometheus.models import ExportModelOperationsMixin
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

from backend.api.models import UserProfile
from backend.static.storage_folders import get_storage_folder_encrypted_record_document
from backend.static.encrypted_storage import EncryptedStorage


class EncryptedRecordDocument(
    ExportModelOperationsMixin("encrypted_record_document"), models.Model
):
    name = models.CharField(max_length=200)
    creator = models.ForeignKey(
        UserProfile,
        related_name="e_record_documents_created",
        on_delete=models.SET_NULL,
        null=True,
    )

    record = models.ForeignKey(
        "EncryptedRecord", related_name="e_record_documents", on_delete=models.CASCADE
    )

    created_on = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now_add=True)

    file_size = models.BigIntegerField()

    tagged = models.ManyToManyField(
        "RecordDocumentTag", related_name="e_tagged", blank=True
    )

    def __str__(self):
        return (
            "e_record_document: "
            + str(self.id)
            + ":"
            + self.name
            + "; creator: "
            + str(self.creator.id)
            + "; record: "
            + str(self.record.id)
        )

    def get_file_key(self):
        return (
            get_storage_folder_encrypted_record_document(
                self.record.from_rlc_id, self.record.id
            )
            + self.name
            + ".enc"
        )

    def get_folder(self):
        return get_storage_folder_encrypted_record_document(
            self.record.from_rlc_id, self.record.id
        )

    def delete_on_cloud(self):
        try:
            EncryptedStorage.delete_on_s3(self.get_file_key())
        except:
            print("couldnt delete " + self.name + " on cloud")

    @receiver(pre_delete)
    def pre_deletion(sender, instance, **kwargs):
        if sender == EncryptedRecordDocument:
            instance.delete_on_cloud()
