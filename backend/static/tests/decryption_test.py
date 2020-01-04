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
        msg = 'secret message. encrypt and decrypt it!'
        key = 'shhh! its a secret!asd'
        iv = AESEncryption.generate_iv()

        encrypted = AESEncryption.encrypt(msg, key, iv)
        decrypted = AESEncryption.decrypt(encrypted, key, iv)

        self.assertEqual(decrypted, msg)

    def test_aes_en_decrypt_long(self):
        msg = 'secret message. encrypt and decrypt it!'
        for i in range(20):
            msg = msg + msg
        key = 'shhh! its a secret!'
        iv = AESEncryption.generate_iv()

        encrypted = AESEncryption.encrypt(msg, key, iv)
        decrypted = AESEncryption.decrypt(encrypted, key, iv)

        self.assertEqual(decrypted, msg)

    def test_aes_en_decrypt_random_1(self):
        msg = os.urandom(512)
        key = os.urandom(100)
        iv = AESEncryption.generate_iv()

        encrypted = AESEncryption.encrypt(msg, key, iv)
        decrypted = AESEncryption.decrypt(encrypted, key, iv, OutputType.BYTES)

        self.assertEqual(decrypted, msg)

    def test_aes_en_decrypt_random_100(self):
        for i in range(100):
            msg = os.urandom(512)
            key = os.urandom(100)
            iv = AESEncryption.generate_iv()

            encrypted = AESEncryption.encrypt(msg, key, iv)
            decrypted = AESEncryption.decrypt(encrypted, key, iv, OutputType.BYTES)

            self.assertEqual(decrypted, msg)

    def test_aes_en_decrypt_random_1000(self):
        for i in range(1000):
            msg = os.urandom(4096)
            key = os.urandom(256)
            iv = AESEncryption.generate_iv()

            encrypted = AESEncryption.encrypt(msg, key, iv)
            decrypted = AESEncryption.decrypt(encrypted, key, iv, OutputType.BYTES)

            self.assertEqual(decrypted, msg)

    def test_aes_en_decrypt_random_1000_hazmat(self):
        for i in range(1000):
            msg = os.urandom(4096)
            key = os.urandom(256)
            iv = AESEncryption.generate_iv()

            encrypted = AESEncryption.encrypt_hazmat(msg, key, iv)
            decrypted = AESEncryption.decrypt_hazmat(encrypted, key, iv, OutputType.BYTES)

            self.assertEqual(decrypted, msg)

    def test_rsa_en_decrypt(self):
        msg = 'really secret message'
        private_key, public_key = RSAEncryption.generate_keys()
        encrypted = RSAEncryption.encrypt(msg, public_key)
        decrypted = RSAEncryption.decrypt(encrypted, private_key)

        self.assertEqual(decrypted, msg)

    def test_rsa_en_decrypt_cryptodome(self):
        msg = 'kjsenf29349nfkse1-2{ad2k'
        private_key, public_key = RSAEncryption.generate_keys_cryptodome()
        encrypted = RSAEncryption.encrypt_cryptodome(msg, public_key)
        decrypted = RSAEncryption.decrypt_cryptodome(encrypted, private_key)

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

    def test_rsa_en_decrypt_random_10_cryptodome(self):
        for i in range(10):
            msg = os.urandom(180)
            private_key, public_key = RSAEncryption.generate_keys_cryptodome()
            encrypted = RSAEncryption.encrypt_cryptodome(msg, public_key)
            decrypted = RSAEncryption.decrypt_cryptodome(encrypted, private_key, OutputType.BYTES)

            self.assertEqual(decrypted, msg)

    @staticmethod
    def test_generate_10_keys_cryptodome():
        for i in range(10):
            RSAEncryption.generate_keys_cryptodome()

    @staticmethod
    def test_generate_10_keys_hazmat():
        for i in range(10):
            RSAEncryption.generate_keys()

    def test_aes_en_decrypt_file(self):
        iv = AESEncryption.generate_iv()
        key = 'secret password'
        AESEncryption.encrypt_file('test_files/test_file.png', key, iv)
        AESEncryption.decrypt_file('test_files/test_file.png.enc', key, iv,
                                   'test_files/test_file_decrypted.png')
        self.assertTrue(filecmp.cmp('test_files/test_file.png', 'test_files/test_file_decrypted.png'))

    def test_aes_en_decrypt_big_file(self):
        iv = AESEncryption.generate_iv()
        key = 'secret password'
        AESEncryption.encrypt_file('test_files/big_file.test', key, iv)
        AESEncryption.decrypt_file('test_files/big_file.test.enc', key, iv,
                                   'test_files/big_file_decrypted.test')
        self.assertTrue(filecmp.cmp('test_files/big_file.test', 'test_files/big_file_decrypted.test'))

    def test_aes_en_decrypt_big_video(self):
        iv = AESEncryption.generate_iv()
        key = 'secret password!sdifu923'
        AESEncryption.encrypt_file('test_files/big_video.mp4', key, iv)
        AESEncryption.decrypt_file('test_files/big_video.mp4.enc', key, iv,
                                   'test_files/big_video_decrypted.mp4')
        self.assertTrue(filecmp.cmp('test_files/big_video.mp4', 'test_files/big_video_decrypted.mp4'))

    def test_aes_wo_iv_en_decrypt(self):
        msg = 'secret message. encrypt and decrypt it!'
        key = 'shhh! its a secret!asd'

        encrypted = AESEncryption.encrypt_wo_iv(msg, key)
        decrypted = AESEncryption.decrypt_wo_iv(encrypted, key)

        self.assertEqual(decrypted, msg)

    def test_aes__wo_iv_en_decrypt_file(self):
        key = 'secret password'
        AESEncryption.encrypt_file_wo_iv('test_files/test_file.png', key)
        AESEncryption.decrypt_file_wo_iv('test_files/test_file.png.enc', key, 'test_files/test_file_decrypted.png')
        self.assertTrue(filecmp.cmp('test_files/test_file.png', 'test_files/test_file_decrypted.png'))

    def test_aes_wo_iv_en_decrypt_big_video(self):
        key = 'secret password!sdifu923'
        AESEncryption.encrypt_file_wo_iv('test_files/big_video.mp4', key)
        AESEncryption.decrypt_file_wo_iv('test_files/big_video.mp4.enc', key, 'test_files/big_video_decrypted.mp4')
        self.assertTrue(filecmp.cmp('test_files/big_video.mp4', 'test_files/big_video_decrypted.mp4'))
