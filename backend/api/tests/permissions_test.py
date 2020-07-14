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
from backend.api.models import UserProfile, Permission, HasPermission, Group, Rlc
from backend.api.tests.statics import StaticTestMethods


class PermissionTests(TransactionTestCase):
    def setUp(self):
        self.client = StaticTestMethods.force_authentication_superuser()
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

    def test_get_real_users_with_permission_for_rlc_1(self):
        rlc = Rlc(name='test rlc')
        rlc.save()

        permission = Permission(name='test_permission')
        permission.save()

        users = StaticTestMethods.generate_users(5, rlc)

        group = Group(name='test_group', from_rlc=rlc, visible=False)
        group.save()
        group.group_members.add(users[0])
        group.group_members.add(users[1])
        group.save()

        has_permission = HasPermission(group_has_permission=group, permission=permission, permission_for_rlc=rlc)
        has_permission.save()

        has_permission = HasPermission(user_has_permission=users[2], permission=permission, permission_for_rlc=rlc)
        has_permission.save()
        has_permission = HasPermission(user_has_permission=users[4], permission=permission, permission_for_rlc=rlc)
        has_permission.save()

        users_with_permissions = permission.get_real_users_with_permission_for_rlc(rlc)

        self.assertTrue(users_with_permissions.__len__() == 4)
        self.assertTrue(users[0] in users_with_permissions)
        self.assertTrue(users[1] in users_with_permissions)
        self.assertTrue(users[2] in users_with_permissions)
        self.assertTrue(users[4] in users_with_permissions)

    def test_get_real_users_with_permission_for_rlc_2(self):
        rlc = Rlc(name='test rlc')
        rlc.save()

        permission = Permission(name='test_permission')
        permission.save()

        users = StaticTestMethods.generate_users(5, rlc)

        has_permission = HasPermission(rlc_has_permission=rlc, permission=permission, permission_for_rlc=rlc)
        has_permission.save()

        users_with_permissions = permission.get_real_users_with_permission_for_rlc(rlc)

        self.assertTrue(users_with_permissions.__len__() == 5)
        self.assertTrue(users[0] in users_with_permissions)
        self.assertTrue(users[1] in users_with_permissions)
        self.assertTrue(users[2] in users_with_permissions)
        self.assertTrue(users[3] in users_with_permissions)
        self.assertTrue(users[4] in users_with_permissions)
