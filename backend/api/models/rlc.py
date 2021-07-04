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
    name = models.CharField(max_length=200, null=False)
    use_record_pool = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        verbose_name = "Rlc"
        verbose_name_plural = "Rlcs"

    def __str__(self):
        return "rlc: {}; name: {};".format(self.pk, self.name)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # create the root folder from files if it doesn't exist
        from backend.files.models import Folder
        if not Folder.objects.filter(rlc=self, parent=None).exists():
            Folder.objects.create(rlc=self, parent=None, name='Files')

    def get_consultants(self):
        """
        gets all user from rlc with permission to consult
        :return:
        """
        users = self.rlc_members.all()
        consultants = []
        for user in list(users):
            if user.has_permission(PERMISSION_CAN_CONSULT):
                consultants.append(user.pk)
        return UserProfile.objects.filter(pk__in=consultants)

    def get_public_key(self) -> bytes:
        # safety check
        if not hasattr(self, "encryption_keys"):
            self.generate_keys()
        # return the public key
        return self.encryption_keys.public_key

    def get_aes_key(
        self, user: UserProfile = None, private_key_user: str = None
    ) -> str:
        if user and private_key_user:
            # get the aes key that encrypted the rlc private key. this aes key is encrypted for every user with its
            # public key, therefore only its private key can unlock the aes key.
            keys = user.users_rlc_keys.get(rlc=self)
            keys.decrypt(private_key_user)
            aes_key = keys.encrypted_key
            return aes_key

        else:
            raise ValueError("You need to set (user and private_key_user).")

    def get_private_key(
        self, user: UserProfile = None, private_key_user: str = None
    ) -> str:
        # safety check
        if not hasattr(self, "encryption_keys"):
            self.generate_keys()

        if user and private_key_user:

            keys = user.users_rlc_keys.get(rlc=self)
            keys.decrypt(private_key_user)
            aes_key = self.get_aes_key(user=user, private_key_user=private_key_user)

            rlc_keys = self.encryption_keys
            rlc_keys.decrypt(aes_key)

            return rlc_keys.encrypted_private_key

        else:
            raise ValueError("You need to pass (user and private_key_user).")

    def generate_keys(self) -> None:
        from backend.api.models.rlc_encryption_keys import RlcEncryptionKeys
        from backend.api.models.users_rlc_keys import UsersRlcKeys

        # safety return
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
            user_rlc_keys = UsersRlcKeys(user=user, rlc=self, encrypted_key=aes_key)
            user_rlc_keys.encrypt(user.get_public_key())
            user_rlc_keys.save()
