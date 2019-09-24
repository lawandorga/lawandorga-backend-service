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
from ..models import UserProfile, Group
from .statics import StaticTestMethods


class GroupsTests(TransactionTestCase):
    def setUp(self):
        self.client = StaticTestMethods.force_authentication()
        self.user = UserProfile.objects.get(email='test123@test.com')
        self.base_url_create = '/api/groups/'

    def test_create_group_success(self):
        before = Group.objects.count()
        response = self.client.post(self.base_url_create, {
            'name': 'The best group',
            'visible': True,
            'group_members': [1]
        })
        after = Group.objects.count()
        self.assertTrue(response.status_code == 201)
        self.assertTrue(before+1 == after)


