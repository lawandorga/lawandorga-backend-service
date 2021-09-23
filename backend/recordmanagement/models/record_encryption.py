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
from backend.recordmanagement.models.encrypted_record import EncryptedRecord
from backend.static.encryption import RSAEncryption, EncryptedModelMixin
from backend.api.models import UserProfile
from django.db import models


class RecordEncryption(EncryptedModelMixin, models.Model):
    user = models.ForeignKey(
        UserProfile, related_name="record_encryptions", on_delete=models.CASCADE
    )
    record = models.ForeignKey(
        EncryptedRecord, related_name="encryptions", on_delete=models.CASCADE
    )
    encrypted_key = models.BinaryField()

    encryption_class = RSAEncryption
    encrypted_fields = ["encrypted_key"]

    class Meta:
        unique_together = ("user", "record")
        verbose_name = "RecordEncryption"
        verbose_name_plural = "RecordEncryptions"

    def __str__(self):
        return "recordEncryption: {}; user: {}; record: {};".format(
            self.id, self.user.email, self.record.record_token
        )

    def save(self, *args, **kwargs):
        if not RecordEncryption.objects.filter(user=self.user, record=self.record).exists():
            super().save(*args, **kwargs)

    def decrypt(self, private_key_user: str = None) -> None:
        if private_key_user:
            key = private_key_user
        else:
            raise ValueError("You need to pass (private_key_user).")
        super().decrypt(key)

    def get_key(self, private_key_user: str) -> str:
        if not self.encrypted_key:
            raise ValueError("This RecordEncryption does not have an encrypted key.")
        return RSAEncryption.decrypt(self.encrypted_key, private_key_user)
