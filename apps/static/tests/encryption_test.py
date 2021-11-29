from apps.static.encryption import AESEncryption, OutputType, RSAEncryption
from django.test import SimpleTestCase
import os


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
        msg = "fdslkjsad320234rnjdlsfjsda£$£$$%////"
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
