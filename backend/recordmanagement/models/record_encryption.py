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

from backend.api.models import UserProfile
from backend.recordmanagement.models import EncryptedRecord
from backend.static.encryption import RSAEncryption


class RecordEncryption(models.Model):
    user = models.ForeignKey(UserProfile, related_name="record_encryptions", on_delete=models.CASCADE, null=False)
    record = models.ForeignKey(EncryptedRecord, related_name="encryptions", on_delete=models.CASCADE, null=False)
    encrypted_key = models.BinaryField()

    def __str__(self):
        return 'record_encryption: ' + str(self.id) + '; user: ' + str(self.user.id) + '; e_record: ' + str(
            self.record.id)

    def decrypt(self, pem_private_key_of_user):
        encrypted_key = self.encrypted_key
        try:
            encrypted_key = encrypted_key.tobytes()
        except:
            pass
        return RSAEncryption.decrypt(encrypted_key, pem_private_key_of_user)
