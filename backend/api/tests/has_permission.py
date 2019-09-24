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
from ..models import UserProfile, Permission, HasPermission, Group
from .fixtures import CreateFixtures
from .statics import StaticTestMethods


class HasPermissionTests(TransactionTestCase):
    def setUp(self):
        self.client = StaticTestMethods.force_authentication()
        self.base_url = '/api/has_permission/'
        CreateFixtures.create_sample_groups()
        CreateFixtures.create_sample_permissions()
        self.user1 = UserProfile.objects.get(email='test123@test.com')
        self.group1 = list(Group.objects.all())[0]
        self.permission = list(Permission.objects.all())[0]

    def test_create_hasPermission_success_user_user(self):
        before = HasPermission.objects.count()
        response = self.client.post(self.base_url, {
            'permission': self.permission.id,
            'user_has_permission': self.user1.id,
            'permission_for_user': self.user1.id
        })
        after = HasPermission.objects.count()

        self.assertTrue(before+1 == after)
        self.assertTrue(response.status_code == 201)

    def test_create_hasPermission_success_user_group(self):
        before = HasPermission.objects.count()
        response = self.client.post(self.base_url, {
            'permission': self.permission.id,
            'user_has_permission': self.user1.id,
            'permission_for_group': self.group1.id
        })
        after = HasPermission.objects.count()

        self.assertTrue(before+1 == after)
        self.assertTrue(response.status_code == 201)

    def test_create_hasPermission_success_group_user(self):
        before = HasPermission.objects.count()
        response = self.client.post(self.base_url, {
            'permission': self.permission.id,
            'group_has_permission': self.group1.id,
            'permission_for_user': self.user1.id
        })
        after = HasPermission.objects.count()

        self.assertTrue(before+1 == after)
        self.assertTrue(response.status_code == 201)

    def test_create_hasPermission_success_group_group(self):
        before = HasPermission.objects.count()
        response = self.client.post(self.base_url, {
            'permission': self.permission.id,
            'group_has_permission': self.group1.id,
            'permission_for_group': self.group1.id
        })
        after = HasPermission.objects.count()

        self.assertTrue(before+1 == after)
        self.assertTrue(response.status_code == 201)

    def test_create_hasPermission_error_double_has(self):
        before = HasPermission.objects.count()
        response = self.client.post(self.base_url, {
            'permission': self.permission.id,
            'user_has_permission': self.user1.id,
            'group_has_permission': self.group1.id,
            'permission_for_group': self.group1.id
        })
        after = HasPermission.objects.count()

        self.assertTrue(before == after)
        self.assertTrue(response.status_code == 400)

    def test_create_hasPermission_error_double_for(self):
        before = HasPermission.objects.count()
        response = self.client.post(self.base_url, {
            'permission': self.permission.id,
            'group_has_permission': self.group1.id,
            'permission_for_user': self.user1.id,
            'permission_for_group': self.group1.id
        })
        after = HasPermission.objects.count()

        self.assertTrue(before == after)
        self.assertTrue(response.status_code == 400)

    def test_create_hasPermission_error_doubled(self):
        before = HasPermission.objects.count()
        to_post = {
            'permission': self.permission.id,
            'group_has_permission': self.group1.id,
            'permission_for_group': self.group1.id
        }
        response = self.client.post(self.base_url, to_post)
        response = self.client.post(self.base_url, to_post)
        after = HasPermission.objects.count()

        self.assertTrue(before + 1 == after)
        self.assertTrue(response.status_code == 409)

    # def test_tttt(self):
    #     perms = CreateFixtures.create_sample_has_permissions()
    #
    #     user = list(UserProfile.objects.filter(email='test123@test.com'))[0]
    #     perms = user.get_as_user_permissions()
    #     p2 = user.get_as_group_member_permissions()
    #     x = user.get_overall_permissions()
    #
    #     pp = user.get_overall_special_permissions('delete_records')
    #     # add and delete
    #     rwer = user.has_as_user_permission(1, for_user=2)
    #     qweq = user.has_as_group_member_permission(3, for_group=2)
    #     qwe = user.has_permission(1, for_user=2)
    #     a = 10
    #
    # def test_ttttttt(self):
    #     perms = CreateFixtures.create_sample_has_permissions()
    #
    #     perm = Permission.objects.first()
    #     UserProfile.objects.get_users_with_special_permission(1, for_user=2)
    #
    #     self.assertTrue(True)
