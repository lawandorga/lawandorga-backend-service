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
from ..models import UserProfile, Group, HasPermission, Permission, Rlc
from .statics import StaticTestMethods


class GroupsTests(TransactionTestCase):
    def setUp(self):
        self.client = StaticTestMethods.force_authentication_superuser()
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
