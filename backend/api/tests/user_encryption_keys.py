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


from django.test import TransactionTestCase
from backend.api.models import UserProfile, UserEncryptionKeys
from backend.api.tests.statics import StaticTestMethods
from backend.static.encryption import RSAEncryption,get_bytes_from_string_or_return_bytes


class UserEncryptionKeysTests(TransactionTestCase):
    def setUp(self):
        pass

    def test_user_encryption_keys_basic_working(self):
        user = StaticTestMethods.generate_test_user()
        keys = StaticTestMethods.generate_user_encryption_keys(user)

        message = 'hello there'
        encrypted = RSAEncryption.encrypt(message, keys.public_key)
        decrypted = RSAEncryption.decrypt(encrypted, keys.private_key)

        self.assertEqual(message, decrypted)

    def test_user_encryption_keys_from_database_working(self):
        user = StaticTestMethods.generate_test_user()
        StaticTestMethods.generate_user_encryption_keys(user)
        keys = UserEncryptionKeys.objects.get(user=user)

        message = 'hello there'
        encrypted = RSAEncryption.encrypt(message, keys.public_key)
        decrypted = RSAEncryption.decrypt(encrypted, keys.private_key)

        self.assertEqual(message, decrypted)

    def test_user_encryption_keys_working_encrypted_private_key(self):
        user = StaticTestMethods.generate_test_user()
        StaticTestMethods.generate_user_encryption_keys(user)
        users_password = 'my secret password kabum'
        keys = UserEncryptionKeys.objects.get(user=user)
        private_key_1_bytes = keys.decrypt_private_key(users_password)
        private_key_2_string = keys.decrypt_private_key(users_password)


        message = 'hello there'
        encrypted = RSAEncryption.encrypt(message, keys.public_key)
        decrypted_1 = RSAEncryption.decrypt(encrypted, private_key_1_bytes)

        # ok to manually convert it, conversion happens in middleware (get_private_key)
        decrypted_2 = RSAEncryption.decrypt(encrypted, get_bytes_from_string_or_return_bytes(private_key_2_string))

        self.assertEqual(message, decrypted_1)
        self.assertEqual(message, decrypted_2)
