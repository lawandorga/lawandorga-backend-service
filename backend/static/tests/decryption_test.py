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

import os
from django.test import SimpleTestCase, TransactionTestCase
from backend.static.encryption import AESEncryption, OutputType, RSAEncryption


class EncryptionTests(SimpleTestCase):
    def test_aes_en_decrypt(self):
        msg = 'secret message. encrypt and decrypt it!'
        key = 'shhh! its a secret!'
        iv = os.urandom(16)

        encrypted = AESEncryption.encrypt(msg, key, iv)
        decrypted = AESEncryption.decrypt(encrypted, key, iv)

        self.assertEqual(decrypted, msg)

    def test_aes_en_decrypt_long(self):
        msg = 'secret message. encrypt and decrypt it!'
        for i in range(20):
            msg = msg + msg
        key = 'shhh! its a secret!'
        iv = os.urandom(16)

        encrypted = AESEncryption.encrypt(msg, key, iv)
        decrypted = AESEncryption.decrypt(encrypted, key, iv)

        self.assertEqual(decrypted, msg)

    def test_aes_en_decrypt_random_100(self):
        for i in range(100):
            msg = os.urandom(512)
            key = os.urandom(100)
            iv = os.urandom(16)

            encrypted = AESEncryption.encrypt(msg, key, iv)
            decrypted = AESEncryption.decrypt(encrypted, key, iv, OutputType.BYTES)

            self.assertEqual(decrypted, msg)

    def test_aes_en_decrypt_random_1000(self):
        for i in range(1000):
            msg = os.urandom(4096)
            key = os.urandom(256)
            iv = os.urandom(16)

            encrypted = AESEncryption.encrypt(msg, key, iv)
            decrypted = AESEncryption.decrypt(encrypted, key, iv, OutputType.BYTES)

            self.assertEqual(decrypted, msg)

    def test_rsa_en_decrypt(self):
        msg = 'really secret message'
        private_key, public_key = RSAEncryption.generate_keys()
        encrypted = RSAEncryption.encrypt(msg, public_key)
        decrypted = RSAEncryption.decrypt(encrypted, private_key)

        self.assertEqual(decrypted, msg)

    def test_rsa_en_decrypt_random(self):
        msg = os.urandom(400)
        private_key, public_key = RSAEncryption.generate_keys()
        encrypted = RSAEncryption.encrypt(msg, public_key)
        decrypted = RSAEncryption.decrypt(encrypted, private_key, OutputType.BYTES)

        self.assertEqual(decrypted, msg)

    def test_rsa_en_decrypt_random_10(self):
        for i in range(10):
            msg = os.urandom(300)
            private_key, public_key = RSAEncryption.generate_keys()
            encrypted = RSAEncryption.encrypt(msg, public_key)
            decrypted = RSAEncryption.decrypt(encrypted, private_key, OutputType.BYTES)

            self.assertEqual(decrypted, msg)
