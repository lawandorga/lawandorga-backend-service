from django.test import TransactionTestCase

from core.seedwork.encryption import RSAEncryption


class UserEncryptionKeysTests(TransactionTestCase):
    def test_user_encryption_keys_basic_working(self):
        private_key, public_key = RSAEncryption.generate_keys()

        message = "hello there"
        encrypted = RSAEncryption.encrypt(message, public_key)
        decrypted = RSAEncryption.decrypt(encrypted, private_key)

        self.assertEqual(message, decrypted)

    def test_user_encryption_keys_from_database_working(self):
        private_key, public_key = RSAEncryption.generate_keys()

        message = "hello there"
        encrypted = RSAEncryption.encrypt(message, public_key)
        decrypted = RSAEncryption.decrypt(encrypted, private_key)

        self.assertEqual(message, decrypted)
