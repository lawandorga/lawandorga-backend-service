from typing import List

from rest_framework.test import APIClient

from apps.core.models import OldUserEncryptionKeys, UserProfile
from apps.static.encryption import RSAEncryption


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
