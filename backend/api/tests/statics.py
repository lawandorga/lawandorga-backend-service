#  rlcapp - record and organization management software for refugee law clinics
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

from ..models import UserProfile
from rest_framework.test import APIClient


class StaticTestMethods:
    @staticmethod
    def force_authentication():
        """
        creates a superuser with a static email and returns the forced authenticated apiClient
        :return: the forced APIClient
        """
        UserProfile.objects.create_superuser(email='test123@test.com', name='XX', password='test123')
        client = APIClient()
        user = UserProfile.objects.get(email='test123@test.com')
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
        user = UserProfile.objects.get(email=user)
        client.force_authenticate(user=user)
        return client
