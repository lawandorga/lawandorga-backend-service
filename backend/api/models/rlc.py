#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
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
from backend.static.permissions import PERMISSION_CAN_CONSULT
from ...static.encryption import AESEncryption, RSAEncryption
from django.db import models
from . import UserProfile, RlcEncryptionKeys, UsersRlcKeys


class Rlc(models.Model):
    creator = models.ForeignKey(
        UserProfile, related_name="rlc_created", on_delete=models.SET_NULL, null=True
    )
    name = models.CharField(max_length=200, null=False)
    uni_tied = models.BooleanField(default=False)
    part_of_umbrella = models.BooleanField(default=True)
    note = models.CharField(max_length=4000, null=True, default="")

    def __str__(self):
        return "rlc: {}:{}".format(self.id, self.name)

    def get_consultants(self):
        """
        gets all user from rlc with permission to consult
        :return:
        """
        return UserProfile.objects.get_users_with_special_permission(
            PERMISSION_CAN_CONSULT, for_rlc=self.id
        )

    def get_public_key(self) -> bytes:
        if not hasattr(self, 'encryption_keys'):
            self.generate_keys()
        return self.encryption_keys.public_key

    def generate_keys(self) -> None:
        if hasattr(self, 'encryption_keys'):
            return
        # generate some keys
        aes_key = AESEncryption.generate_secure_key()
        private, public = RSAEncryption.generate_keys()
        encrypted_private = AESEncryption.encrypt(private, aes_key)
        # create encryption key for rlc
        RlcEncryptionKeys.objects.create(
            rlc=self,
            encrypted_private_key=encrypted_private,
            public_key=public
        )
        # create encryption keys for users to be able to decrypt rlc private key with users private key
        # the aes key is encrypted with the users public key, but only the user's private key can decrypt
        # the encrypted aes key
        for user in self.rlc_members.all():
            encrypted_aes_key = RSAEncryption.encrypt(aes_key, user.get_public_key())
            user_rlc_keys = UsersRlcKeys(user=user, rlc=self, encrypted_key=encrypted_aes_key)
            user_rlc_keys.save()
