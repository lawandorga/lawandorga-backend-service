from django.test import SimpleTestCase

from apps.seedwork.encryption import AESEncryption, RSAEncryption


class EncryptionTests(SimpleTestCase):
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
        msg = "12301320931290"
        private_key, public_key = RSAEncryption.generate_keys()
        encrypted = RSAEncryption.encrypt(msg, public_key)
        decrypted = RSAEncryption.decrypt(encrypted, private_key)
        self.assertEqual(decrypted, msg)

    def test_rsa_en_decrypt_random_10(self):
        for i in range(10):
            msg = "sdafdsafdsafdasfdsa{}".format(i)
            private_key, public_key = RSAEncryption.generate_keys()
            encrypted = RSAEncryption.encrypt(msg, public_key)
            decrypted = RSAEncryption.decrypt(encrypted, private_key)

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
