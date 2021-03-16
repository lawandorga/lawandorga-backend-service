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
from backend.static.encryption import RSAEncryption
from backend.api.models import UserProfile
from django.db import models


class RecordEncryption(models.Model):
    user = models.ForeignKey(UserProfile, related_name="record_encryptions", on_delete=models.CASCADE)
    record = models.ForeignKey(EncryptedRecord, related_name="encryptions", on_delete=models.CASCADE)
    encrypted_key = models.BinaryField()

    encrypted_fields = ['encrypted_key']

    class Meta:
        unique_together = ('user', 'record')

    def __str__(self):
        return 'record_encryption: {}; user: {}; encrypted_record: {};'.format(
            self.id, self.user.id, self.record.id
        )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        for field in self.encrypted_fields:
            data_in_field = getattr(self, field)
            if data_in_field and not isinstance(data_in_field, bytes):
                raise ValueError(
                    'The field {} of object {} is not encrypted. Do not save unencrypted data.'.format(field, self))
        super().save(force_insert, force_update, using, update_fields)

    def encrypt(self, public_key_user: bytes) -> None:
        for field in self.encrypted_fields:
            encrypted_field = RSAEncryption.encrypt(getattr(self, field), public_key_user)
            setattr(self, field, encrypted_field)

    def decrypt(self, private_key_user: str) -> None:
        for field in self.encrypted_fields:
            decrypted_field = RSAEncryption.decrypt(getattr(self, field), private_key_user)
            setattr(self, field, decrypted_field)

    def get_key(self, private_key_user: str) -> str:
        if not self.encrypted_key:
            raise ValueError('This RecordEncryption does not have an encrypted key.')
        return RSAEncryption.decrypt(self.encrypted_key, private_key_user)
