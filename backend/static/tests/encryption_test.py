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

import filecmp
import os

from django.test import SimpleTestCase

from backend.static.encryption import AESEncryption, OutputType, RSAEncryption


class EncryptionTests(SimpleTestCase):
    def test_aes_en_decrypt(self):
        msg = "secret message. encrypt and decrypt it!"
        key = "shhh! its a secret!asd"
        iv = AESEncryption.generate_iv()

        encrypted = AESEncryption.encrypt_with_iv(msg, key, iv)
        decrypted = AESEncryption.decrypt_with_iv(encrypted, key, iv)

        self.assertEqual(decrypted, msg)

    def test_aes_en_decrypt_long(self):
        msg = "secret message. encrypt and decrypt it!"
        for i in range(20):
            msg = msg + msg
        key = "shhh! its a secret!"
        iv = AESEncryption.generate_iv()

        encrypted = AESEncryption.encrypt_with_iv(msg, key, iv)
        decrypted = AESEncryption.decrypt_with_iv(encrypted, key, iv)

        self.assertEqual(decrypted, msg)

    def test_aes_en_decrypt_random_1(self):
        msg = os.urandom(512)
        key = os.urandom(100)
        iv = AESEncryption.generate_iv()

        encrypted = AESEncryption.encrypt_with_iv(msg, key, iv)
        decrypted = AESEncryption.decrypt_with_iv(encrypted, key, iv, OutputType.BYTES)

        self.assertEqual(decrypted, msg)

    def test_aes_en_decrypt_random_100(self):
        for i in range(100):
            msg = os.urandom(512)
            key = os.urandom(100)
            iv = AESEncryption.generate_iv()

            encrypted = AESEncryption.encrypt_with_iv(msg, key, iv)
            decrypted = AESEncryption.decrypt_with_iv(
                encrypted, key, iv, OutputType.BYTES
            )

            self.assertEqual(decrypted, msg)

    def test_aes_en_decrypt_random_1000(self):
        for i in range(1000):
            msg = os.urandom(4096)
            key = os.urandom(256)
            iv = AESEncryption.generate_iv()

            encrypted = AESEncryption.encrypt_with_iv(msg, key, iv)
            decrypted = AESEncryption.decrypt_with_iv(
                encrypted, key, iv, OutputType.BYTES
            )

            self.assertEqual(decrypted, msg)

    def test_rsa_en_decrypt(self):
        msg = "really secret message"
        private_key, public_key = RSAEncryption.generate_keys()
        encrypted = RSAEncryption.encrypt(msg, public_key)
        decrypted = RSAEncryption.decrypt(encrypted, private_key)

        self.assertEqual(decrypted, msg)

    def test_rsa_en_decrypt_real_world(self):
        msg = 'fdslkjsad320234rnjdlsfjsda£$£$$%////'
        private_key, public_key = RSAEncryption.generate_keys()
        encrypted = RSAEncryption.encrypt(msg, public_key)
        decrypted = RSAEncryption.decrypt(encrypted, private_key)

        self.assertEqual(decrypted, msg)

    def test_rsa_en_decrypt_random(self):
        msg = os.urandom(180)
        private_key, public_key = RSAEncryption.generate_keys()
        encrypted = RSAEncryption.encrypt(msg, public_key)
        decrypted = RSAEncryption.decrypt(encrypted, private_key, OutputType.BYTES)

        self.assertEqual(decrypted, msg)

    def test_rsa_en_decrypt_random_10(self):
        for i in range(10):
            msg = os.urandom(180)
            private_key, public_key = RSAEncryption.generate_keys()
            encrypted = RSAEncryption.encrypt(msg, public_key)
            decrypted = RSAEncryption.decrypt(encrypted, private_key, OutputType.BYTES)

            self.assertEqual(decrypted, msg)

    @staticmethod
    def test_generate_10_keys_hazmat():
        for i in range(10):
            RSAEncryption.generate_keys()

    def test_aes_wo_iv_en_decrypt(self):
        msg = "secret message. encrypt and decrypt it!"
        key = "shhh! its a secret!asd"

        encrypted = AESEncryption.encrypt(msg, key)
        decrypted = AESEncryption.decrypt(encrypted, key)

        self.assertEqual(decrypted, msg)

    def test_aes__wo_iv_en_decrypt_file(self):
        key = "secret password"
        AESEncryption.encrypt_file("test_files/test_file.png", key)
        AESEncryption.decrypt_file(
            "test_files/test_file.png.enc", key, "test_files/test_file_decrypted.png"
        )
        self.assertTrue(
            filecmp.cmp(
                "test_files/test_file.png", "test_files/test_file_decrypted.png"
            )
        )

    def test_aes_wo_iv_en_decrypt_big_video(self):
        key = "secret password!sdifu923"
        AESEncryption.encrypt_file("test_files/big_video.mp4", key)
        AESEncryption.decrypt_file(
            "test_files/big_video.mp4.enc", key, "test_files/big_video_decrypted.mp4"
        )
        self.assertTrue(
            filecmp.cmp(
                "test_files/big_video.mp4", "test_files/big_video_decrypted.mp4"
            )
        )

    def test_encrypt_field(self):
        class ClassWithSecrets:
            def __init__(self, preset=0):
                if preset == 2:
                    self.secret_field_1 = "secret1"
                    self.secret_field_2 = "secret1"
                    self.field = "not so secret"
                if preset == 1:
                    self.secret_field_1 = ""
                    self.secret_field_2 = ""
                    self.field = ""

        not_encrypted = ClassWithSecrets(2)
        encrypted = ClassWithSecrets(1)
        key = "kerkekrkerk!"

        AESEncryption.encrypt_field(not_encrypted, encrypted, "secret_field_1", key)
        AESEncryption.encrypt_field(not_encrypted, encrypted, "secret_field_2", key)
        # should do nothing
        AESEncryption.encrypt_field(not_encrypted, encrypted, "secret_field_3", key)

        self.assertTrue(getattr(encrypted, "secret_field_3", None) is None)
        self.assertEqual(
            AESEncryption.decrypt(getattr(encrypted, "secret_field_1"), key),
            getattr(not_encrypted, "secret_field_1"),
        )
        self.assertEqual(
            AESEncryption.decrypt(getattr(encrypted, "secret_field_2"), key),
            getattr(not_encrypted, "secret_field_2"),
        )

    def test_encrypt_field_self(self):
        class ClassWithSecrets:
            def __init__(self, preset=0):
                if preset == 2:
                    self.secret_field_1 = "secret1"
                    self.secret_field_2 = "secret2"
                    self.field = "not so secret"
                if preset == 1:
                    self.secret_field_1 = ""
                    self.secret_field_2 = ""
                    self.field = ""

        source_ception = ClassWithSecrets(2)
        key = "kerkekrkerk!"

        AESEncryption.encrypt_field(
            source_ception, source_ception, "secret_field_1", key
        )
        AESEncryption.encrypt_field(
            source_ception, source_ception, "secret_field_2", key
        )
        # should do nothing
        AESEncryption.encrypt_field(
            source_ception, source_ception, "secret_field_3", key
        )

        self.assertEqual(
            AESEncryption.decrypt(getattr(source_ception, "secret_field_1"), key),
            "secret1",
        )
        self.assertEqual(
            AESEncryption.decrypt(getattr(source_ception, "secret_field_2"), key),
            "secret2",
        )
