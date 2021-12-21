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
from apps.api.models.rlc import Rlc
from apps.api.models.user import UserProfile
from apps.static.encryption import EncryptedModelMixin, RSAEncryption
from django.db import models


class UsersRlcKeys(EncryptedModelMixin, models.Model):
    user = models.ForeignKey(
        UserProfile, related_name="users_rlc_keys", on_delete=models.CASCADE, null=False
    )
    rlc = models.ForeignKey(
        Rlc,
        related_name="encrypted_users_rlc_keys",
        on_delete=models.CASCADE,
        null=False,
    )
    encrypted_key = models.BinaryField()

    encryption_class = RSAEncryption
    encrypted_fields = ["encrypted_key"]

    class Meta:
        verbose_name = "UserRlcKeys"
        verbose_name_plural = "UsersRlcKeys"
        unique_together = ("user", "rlc")

    def __str__(self):
        return "userRlcKeys: {}; user: {}; rlc: {};".format(
            self.pk, self.user.email, self.rlc.name
        )

    def decrypt(self, private_key_user: str) -> None:
        super().decrypt(private_key_user)

    def encrypt(self, public_key_user: str) -> None:
        super().encrypt(public_key_user)