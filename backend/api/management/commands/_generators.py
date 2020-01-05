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

from backend.api.models import UserProfile, EncryptionKeys
from backend.static.encryption import RSAEncryption


class OneTimeGenerators:
    @staticmethod
    def generate_encryption_keys_for_all_users():
        users = UserProfile.objects.all()
        for user in users:
            if EncryptionKeys.objects.filter(user=user):
                continue
            private, public = RSAEncryption.generate_keys()
            user_keys = EncryptionKeys(user=user, private_key=private, public_key=public)
            user_keys.save()
        keys = EncryptionKeys.objects.all()
        a = 10
