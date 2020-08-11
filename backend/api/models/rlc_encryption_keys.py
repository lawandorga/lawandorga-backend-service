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

from backend.api.models import Rlc
from backend.static.error_codes import ERROR__API__RLC__NO_PUBLIC_KEY_FOUND
from backend.api.errors import CustomError
from backend.static.encryption import AESEncryption


class RlcEncryptionKeysQuerySet(models.QuerySet):
    def get_rlcs_public_key(self, rlc):
        try:
            keys = self.get(rlc=rlc)
        except Exception:
            raise CustomError(ERROR__API__RLC__NO_PUBLIC_KEY_FOUND)
        return keys.public_key


class RlcEncryptionKeys(models.Model):
    rlc = models.OneToOneField(
        Rlc, related_name="encryption_keys", on_delete=models.CASCADE
    )
    public_key = models.BinaryField()
    encrypted_private_key = models.BinaryField()

    objects = RlcEncryptionKeysQuerySet.as_manager()

    def decrypt_private_key(self, key_to_encrypt):
        encrypted_private_key = self.encrypted_private_key
        try:
            encrypted_private_key = encrypted_private_key.tobytes()
        except:
            pass
        return AESEncryption.decrypt(encrypted_private_key, key_to_encrypt)
