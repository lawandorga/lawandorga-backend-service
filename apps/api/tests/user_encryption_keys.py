from apps.api.tests.statics import StaticTestMethods
from apps.static.encryption import RSAEncryption, get_bytes_from_string_or_return_bytes
from apps.api.models import UserEncryptionKeys
from django.test import TransactionTestCase


class UserEncryptionKeysTests(TransactionTestCase):
    def setUp(self):
        pass

    def test_user_encryption_keys_basic_working(self):
        user = StaticTestMethods.generate_test_user()
        keys = StaticTestMethods.generate_user_encryption_keys(user)

        message = "hello there"
        encrypted = RSAEncryption.encrypt(message, keys.public_key)
        decrypted = RSAEncryption.decrypt(encrypted, keys.private_key)

        self.assertEqual(message, decrypted)

    def test_user_encryption_keys_from_database_working(self):
        user = StaticTestMethods.generate_test_user()
        StaticTestMethods.generate_user_encryption_keys(user)
        keys = UserEncryptionKeys.objects.get(user=user)

        message = "hello there"
        encrypted = RSAEncryption.encrypt(message, keys.public_key)
        decrypted = RSAEncryption.decrypt(encrypted, keys.private_key)

        self.assertEqual(message, decrypted)

