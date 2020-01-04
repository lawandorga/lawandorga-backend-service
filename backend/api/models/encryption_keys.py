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
from backend.static.encryption import AESEncryption


class EncryptionKeys(models.Model):
    user = models.ForeignKey(UserProfile, related_name="encryption_keys", on_delete=models.CASCADE, null=False)
    private_key = models.BinaryField()
    private_key_encrypted = models.BooleanField(default=False)
    public_key = models.BinaryField()

    def decrypt_private_key(self, key_to_encrypt):
        if self.private_key_encrypted:
            return AESEncryption.decrypt_wo_iv(self.private_key, key_to_encrypt)
        else:
            priv_key = self.private_key
            self.private_key = AESEncryption.encrypt_wo_iv(self.private_key, key_to_encrypt)
            self.private_key_encrypted = True
            self.save()


