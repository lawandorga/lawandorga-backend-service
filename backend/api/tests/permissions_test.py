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

from django.test import TransactionTestCase
from ..models import UserProfile, Permission
from .statics import StaticTestMethods


class PermissionTests(TransactionTestCase):
    def setUp(self):
        self.client = StaticTestMethods.force_authentication()
        self.user = UserProfile.objects.get(email='test123@test.com')
        self.base_url = '/api/permissions/'

    def test_create_new_permission_success(self):
        before = Permission.objects.count()
        response = self.client.post(self.base_url, {
            'name': 'delete all'
        })
        after = Permission.objects.count()
        self.assertTrue(response.status_code == 201)
        self.assertTrue(before+1 == after)

    def test_create_new_permission_error_double(self):
        before = Permission.objects.count()
        to_post = {
            'name': 'delete all'
        }
        self.client.post(self.base_url, to_post)
        response = self.client.post(self.base_url, to_post)
        after = Permission.objects.count()
        self.assertTrue(response.status_code == 400)
        self.assertTrue(before+1 == after)

