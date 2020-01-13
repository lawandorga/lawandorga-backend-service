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
from backend.static.encryption import RSAEncryption


class EncryptedClient(models.Model):
    from_rlc = models.ForeignKey(Rlc, related_name='e_client_from_rlc', on_delete=models.SET_NULL, null=True)
    created_on = models.DateField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now_add=True)

    birthday = models.DateField(null=True, blank=True)
    origin_country = models.ForeignKey('OriginCountry', related_name='e_clients', on_delete=models.SET_NULL, null=True)

    # encrypted
    name = models.BinaryField(null=True)
    note = models.BinaryField(null=True)
    phone_number = models.BinaryField(null=True)

    encrypted_client_key = models.BinaryField(null=True)

    def __str__(self):
        return 'e_client: ' + str(self.id)

    def get_password(self, rlcs_private_key):
        return RSAEncryption.decrypt(self.encrypted_client_key, rlcs_private_key)
