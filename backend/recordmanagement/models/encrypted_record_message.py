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

from backend.api.models import UserProfile
from backend.api.models.notification import Notification
from backend.recordmanagement.models.encrypted_record import EncryptedRecord
from backend.static.encryption import AESEncryption, EncryptedModelMixin


class EncryptedRecordMessageManager(models.Manager):
    """
    Manager for Encrypted Record Messages
    provides methods for whole query table and 'static' class methods
    """

    @staticmethod
    def create_encrypted_record_message(
        sender: UserProfile,
        message: str,
        record: EncryptedRecord,
        senders_private_key: bytes,
    ) -> ("EncryptedRecordMessage", str):
        """
        creates a new encrypted record message for given record
        also creates corresponding notifications

        :param sender: sender of message
        :param message: unencrypted content of message
        :param record: record where message belongs to
        :param senders_private_key: private key of sender to encrypt message
        :return:
        """
        # create message and saves
        record_key = record.get_decryption_key(sender, senders_private_key)
        encrypted_message = AESEncryption.encrypt(message, record_key)
        new_message = EncryptedRecordMessage(
            sender=sender, message=encrypted_message, record=record
        )
        new_message.save()

        Notification.objects.notify_record_message_added(sender, new_message)
        return new_message, record_key


class EncryptedRecordMessage(
    ExportModelOperationsMixin("encrypted_record_message"),
    EncryptedModelMixin,
    models.Model,
):
    created_on = models.DateTimeField(auto_now_add=True)
    #
    sender = models.ForeignKey(
        UserProfile,
        related_name="e_record_messages_sent",
        on_delete=models.SET_NULL,
        null=True,
    )
    record = models.ForeignKey(
        "EncryptedRecord", related_name="messages", on_delete=models.CASCADE
    )

    # encrypted
    message = models.BinaryField(null=False)

    encryption_class = AESEncryption
    encrypted_fields = ["message"]

    objects = EncryptedRecordMessageManager()

    class Meta:
        verbose_name = "RecordMessage"
        verbose_name_plural = "RecordMessages"

    def __str__(self):
        return "recordMessage: {}; record: {};".format(
            self.pk, self.record.record_token
        )

    def encrypt(
        self,
        user: UserProfile = None,
        private_key_user: bytes = None,
        aes_key: str = None,
    ) -> None:
        if user and private_key_user:
            record_encryption = self.record.encryptions.get(user=user)
            record_encryption.decrypt(private_key_user)
            key = record_encryption.encrypted_key
        elif aes_key:
            key = aes_key
        else:
            raise ValueError(
                "You have to set (user and private_key_user) or (aes_key)."
            )
        super().encrypt(key)

    def decrypt(self, user: UserProfile = None, private_key_user: bytes = None) -> None:
        if user and private_key_user:
            record_encryption = self.record.encryptions.get(user=user)
            record_encryption.decrypt(private_key_user)
            key = record_encryption.encrypted_key
        else:
            raise ValueError("You have to set (user and private_key_user).")
        super().decrypt(key)

    def __str__(self):
        return "encrypted_record_message: {}; encrypted_record: {}; sender: {};".format(
            self.pk, self.record.pk, self.sender.pk
        )
