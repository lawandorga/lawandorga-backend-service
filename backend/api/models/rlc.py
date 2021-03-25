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
from backend.static.encryption import AESEncryption, RSAEncryption
from backend.api.models.user import UserProfile
from django.db import models


class Rlc(models.Model):
    creator = models.ForeignKey(
        UserProfile, related_name="rlc_created", on_delete=models.SET_NULL, null=True
    )
    name = models.CharField(max_length=200, null=False)
    uni_tied = models.BooleanField(default=False)
    part_of_umbrella = models.BooleanField(default=True)
    note = models.CharField(max_length=4000, null=True, default="")

    class Meta:
        verbose_name = 'Rlc'
        verbose_name_plural = 'Rlcs'

    def __str__(self):
        return "rlc: {}; name: {};".format(self.pk, self.name)

    def get_consultants(self):
        """
        gets all user from rlc with permission to consult
        :return:
        """
        return UserProfile.objects.get_users_with_special_permission(
            PERMISSION_CAN_CONSULT, for_rlc=self.id
        )

    def get_public_key(self) -> bytes:
        # safety check
        if not hasattr(self, "encryption_keys"):
            self.generate_keys()
        # return the public key
        return self.encryption_keys.public_key

    def get_private_key(self, user: UserProfile, user_private_key: bytes):
        from backend.api.models.users_rlc_keys import UsersRlcKeys

        # safety check
        if not hasattr(self, "encryption_keys"):
            self.generate_keys()

        # get the aes key that encrypted the rlc private key. this aes key is encrypted for every user with its
        # public key, therefore only its private key can unlock the aes key.
        keys = UsersRlcKeys.objects.get(user=user, rlc=self)
        keys.decrypt(user_private_key)
        aes_key = keys.encrypted_key

        rlc_keys = self.encryption_keys
        rlc_keys.decrypt(aes_key)

        return rlc_keys.encrypted_private_key

    def generate_keys(self) -> None:
        from backend.api.models.rlc_encryption_keys import RlcEncryptionKeys
        from backend.api.models.users_rlc_keys import UsersRlcKeys

        if hasattr(self, "encryption_keys"):
            return
        # generate some keys
        aes_key = AESEncryption.generate_secure_key()
        private, public = RSAEncryption.generate_keys()
        encrypted_private = AESEncryption.encrypt(private, aes_key)
        # create encryption key for rlc
        RlcEncryptionKeys.objects.create(
            rlc=self, encrypted_private_key=encrypted_private, public_key=public
        )
        # create encryption keys for users to be able to decrypt rlc private key with users private key
        # the aes key is encrypted with the users public key, but only the user's private key can decrypt
        # the encrypted aes key
        for user in self.rlc_members.all():
            encrypted_aes_key = RSAEncryption.encrypt(aes_key, user.get_public_key())
            user_rlc_keys = UsersRlcKeys(
                user=user, rlc=self, encrypted_key=encrypted_aes_key
            )
            user_rlc_keys.save()
