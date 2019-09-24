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

from rest_framework.test import APIClient
from django.test import TransactionTestCase
from ..models import UserProfile, Rlc
from .fixtures import CreateFixtures
from .statics import StaticTestMethods
from rest_framework.authtoken.models import Token


class RlcsTest(TransactionTestCase):
    def setUp(self):
        self.client = StaticTestMethods.force_authentication()
        self.base_url = '/api/rlcs/'
        self.base_list_url = '/api/get_rlcs/'

    def test_list_rlcs_without_authentication(self):
        CreateFixtures.add_rlc(1, 'muenchen', [], True, True, '')
        CreateFixtures.add_rlc(2, 'hamburg', [], True, True, '')

        client = APIClient()
        response = client.get(self.base_list_url)

        self.assertTrue(response.data.__len__() == 2)

