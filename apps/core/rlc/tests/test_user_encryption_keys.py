from django.test import TransactionTestCase

from apps.core.auth.models import UserProfile
from apps.core.models import OldUserEncryptionKeys
from apps.seedwork.encryption import RSAEncryption


class StaticTestMethods:
    @staticmethod
    def generate_test_user(rlc=None):
        user = UserProfile(name="test_user_1", email="test_user@web.de")
        if rlc:
            user.rlc = rlc
        user.save()
        return user

    @staticmethod
    def generate_user_encryption_keys(user):
        private, public = RSAEncryption.generate_keys()
        keys = OldUserEncryptionKeys(user=user, private_key=private, public_key=public)
        keys.save()
        return keys


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
        keys = OldUserEncryptionKeys.objects.get(user=user)

        message = "hello there"
        encrypted = RSAEncryption.encrypt(message, keys.public_key)
        decrypted = RSAEncryption.decrypt(encrypted, keys.private_key)

        self.assertEqual(message, decrypted)
