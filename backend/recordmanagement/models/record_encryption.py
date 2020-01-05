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
from backend.recordmanagement.models import Record
from backend.static.encryption import RSAEncryption


class RecordEncryption(models.Model):
    user = models.ForeignKey(UserProfile, related_name="record_encryptions", on_delete=models.CASCADE, null=False)
    record = models.ForeignKey(Record, related_name="encryptions", on_delete=models.CASCADE, null=False)
    encrypted_key = models.BinaryField()

    def decrypt(self, pem_private_key_of_user):
        return RSAEncryption.decrypt(self.encrypted_key, pem_private_key_of_user)
