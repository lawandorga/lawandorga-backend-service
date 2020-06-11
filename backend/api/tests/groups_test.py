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

from django.test import TransactionTestCase

from backend.api.tests.fixtures_encryption import CreateFixtures
from .statics import StaticTestMethods
from backend.api.models import Group, HasPermission, Permission, Rlc, UserProfile
from backend.static.permissions import PERMISSION_MANAGE_GROUPS_RLC

class GroupsTests(TransactionTestCase):
    def setUp(self):
        self.base_fixtures = CreateFixtures.create_base_fixtures()
        self.superuser = CreateFixtures.create_superuser()
        self.client = StaticTestMethods.force_authentication_superuser()
        self.user = UserProfile.objects.get(email='test123@test.com')
        self.base_url_create = '/api/groups/'

    def test_create_group_success(self):
        before = Group.objects.count()
        response = self.superuser['client'].post(self.base_url_create, {
            'name': 'The best group',
            'visible': True,
            'group_members': [1]
        })
        after = Group.objects.count()
        self.assertTrue(response.status_code == 200)
        self.assertTrue(before + 1 == after)

    def test_has_group_permission(self):
        perm1 = Permission(name='test_permission_1')
        perm1.save()
        perm2 = Permission(name='test_permission_2')
        perm2.save()
        rlc = Rlc(name='test rlc1')
        rlc.save()
        group = Group(from_rlc=rlc, name='test group 1', visible=True)
        group.save()

        hasperm1 = HasPermission(group_has_permission=group, permission=perm1, permission_for_rlc=rlc)
        hasperm1.save()
        group = Group.objects.first()
        self.assertTrue(group.has_group_permission(perm1))
        self.assertTrue(group.has_group_permission(perm1.name))

    def test_has_group_one_permission(self):
        perm1 = Permission(name='test_permission_1')
        perm1.save()
        perm2 = Permission(name='test_permission_2')
        perm2.save()
        rlc = Rlc(name='test rlc1')
        rlc.save()
        group = Group(from_rlc=rlc, name='test group 1', visible=True)
        group.save()

        hasperm1 = HasPermission(group_has_permission=group, permission=perm1, permission_for_rlc=rlc)
        hasperm1.save()
        group = Group.objects.first()
        self.assertTrue(group.has_group_one_permission([perm1, perm2]))

    def test_has_group_one_permission_2(self):
        perm1 = Permission(name='test_permission_1')
        perm1.save()
        perm2 = Permission(name='test_permission_2')
        perm2.save()
        rlc = Rlc(name='test rlc1')
        rlc.save()
        group = Group(from_rlc=rlc, name='test group 1', visible=True)
        group.save()

        hasperm1 = HasPermission(group_has_permission=group, permission=perm1, permission_for_rlc=rlc)
        hasperm1.save()
        group = Group.objects.first()
        self.assertTrue(not group.has_group_one_permission([perm2]))

    def test_add_group_members(self):
        # manage groups
        CreateFixtures.add_permission_for_user(self.base_fixtures['users'][0]['user'], PERMISSION_MANAGE_GROUPS_RLC)
        old_number_of_users = self.base_fixtures['groups'][0].group_members.count()

        response = self.base_fixtures['users'][0]['client'].post('/api/group_members/', {
            'action': 'add',
            'group_id': self.base_fixtures['groups'][0].id,
            'user_ids': [self.base_fixtures['users'][2]['user'].id, self.base_fixtures['users'][3]['user'].id]
        }, format='json', **{'HTTP_PRIVATE_KEY': self.base_fixtures['users'][0]['private']})

        self.assertEqual(200, response.status_code)
        self.assertEqual(old_number_of_users + 2, self.base_fixtures['groups'][0].group_members.count())

        response = self.base_fixtures['users'][0]['client'].post('/api/group_members/', {
            'action': 'remove',
            'group_id': self.base_fixtures['groups'][0].id,
            'user_ids': [self.base_fixtures['users'][2]['user'].id, self.base_fixtures['users'][3]['user'].id]
        }, format='json')
        self.assertTrue(200, response.status_code)
        self.assertEqual(old_number_of_users, self.base_fixtures['groups'][0].group_members.count())
