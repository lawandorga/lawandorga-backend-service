from rest_framework.test import APIClient

from apps.core.models import OldUserEncryptionKeys, UserProfile
from apps.static.encryption import RSAEncryption


class StaticTestMethods:
    @staticmethod
    def force_authentication_superuser():
        """
        creates a superuser with a static email and returns the forced authenticated apiClient
        :return: the forced APIClient
        """
        UserProfile.objects.create(
            email="test123@test.com",
            name="XX",
            password="test123",
            is_superuser=True,
            is_staff=True,
        )
        client = APIClient()
        user = UserProfile.objects.get(email="test123@test.com")
        client.force_authenticate(user=user)
        return client

    @staticmethod
    def force_authentication_with_user_email(user):
        """
        authenticates a given user and returns the corresponding APIClient
        :param user: string, email address of the user which should be authenticated
        :return: corresponding apiClient
        """
        client = APIClient()
        user = UserProfile.objects.get(email=user)
        client.force_authenticate(user=user)
        return client

    @staticmethod
    def force_authentication_with_user(user):
        """
        authenticates a given user and returns the corresponding APIClient
        :param user: string, email address of the user which should be authenticated
        :return: corresponding apiClient
        """
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    @staticmethod
    def generate_users(number_of_users, rlc) -> [UserProfile]:
        base_name = "test_user"
        users = []
        for i in range(number_of_users):
            name = base_name + str(i)
            email = name + "@web.de"
            user = UserProfile(email=email, name=name)
            if rlc:
                user.rlc = rlc
            user.save()
            users.append(user)
        return users

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
