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

from rest_framework.test import APIClient
from backend.api.models import UserProfile, UserEncryptionKeys
from backend.static.encryption import RSAEncryption


class StaticTestMethods:
    @staticmethod
    def force_authentication_superuser():
        """
        creates a superuser with a static email and returns the forced authenticated apiClient
        :return: the forced APIClient
        """
        UserProfile.objects.create(
            email="test123@test.com", name="XX", password="test123", is_superuser = True, is_staff=True
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
        keys = UserEncryptionKeys(user=user, private_key=private, public_key=public)
        keys.save()
        return keys
