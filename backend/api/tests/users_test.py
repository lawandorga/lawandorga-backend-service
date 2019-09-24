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


class UsersTests(TransactionTestCase):
    def setUp(self):
        self.client = StaticTestMethods.force_authentication()
        self.user = UserProfile.objects.get(email='test123@test.com')
        self.base_url_create = '/api/create_profile/'
        self.base_url_profile = '/api/profiles/'
        # CreateFixtures.create_sample_countries()

    @staticmethod
    def fixtures_has_permissions():
        CreateFixtures.add_users(((62, 'AA@web.de', 'AA', 'qwe'),
                                  (63, 'BB@web.de', 'BB', 'qwe'),
                                  (64, 'CC@web.de', 'CC', 'qwe'),
                                  (65, 'DD@web.de', 'DD', 'qwe')))
        CreateFixtures.add_groups(((72, 'GroupA', True, [62, 63]),
                                   (73, 'GroupB', True, [63, 64]),
                                   (74, 'GroupC', True, [64, 65])))
        CreateFixtures.add_rlcs(((91, 'RlcA', [62, 63], True, True, 'note1'),
                                 (92, 'RlcB', [64, 65], True, True, 'note2')))
        CreateFixtures.add_groups_to_rlcs(((72, 91),
                                           (73, 92),
                                           (74, 91)))
        CreateFixtures.add_permissions(((1030, 'edit'),
                                        (1031, 'jump'),
                                        (1032, 'can'),
                                        (1033, 'go'),
                                        (1040, 'delete'),
                                        (1041, 'lift'),
                                        (1042, 'wish'),
                                        (1043, 'borrow'),
                                        (1050, 'add'),
                                        (1060, 'remove'),
                                        (1070, 'change'),
                                        (1080, 'look'),
                                        (1090, 'view'),
                                        (1100, 'see'),
                                        (1110, 'show'),
                                        (1120, 'erase'),
                                        (1130, 'can_consult')))

        # user - user 103x
        # group - user 104x
        # user - group 105x
        # group - group 106x
        # user - rlc 107x
        # rlc - user 108x
        # group - rlc 109x
        # rlc - group 110x
        # rlc - rlc 111x
        # user - rlc, user 112x
        # user, group - rlc 113x
        CreateFixtures.add_has_permission(1, 1030, user_has=62, for_user=63)
        CreateFixtures.add_has_permission(2, 1031, user_has=63, for_user=62)
        CreateFixtures.add_has_permission(3, 1032, user_has=63, for_user=64)
        CreateFixtures.add_has_permission(4, 1033, user_has=65, for_user=63)
        CreateFixtures.add_has_permission(5, 1040, group_has=72, for_user=64)
        CreateFixtures.add_has_permission(6, 1041, group_has=73, for_user=64)
        CreateFixtures.add_has_permission(7, 1042, group_has=73, for_user=63)
        CreateFixtures.add_has_permission(8, 1043, group_has=74, for_user=63)
        CreateFixtures.add_has_permission(9, 1050, user_has=62, for_group=73)
        CreateFixtures.add_has_permission(10, 1060, group_has=74, for_group=74)
        CreateFixtures.add_has_permission(11, 1070, user_has=64, for_rlc=91)
        CreateFixtures.add_has_permission(12, 1120, user_has=65, for_rlc=91)
        CreateFixtures.add_has_permission(13, 1120, user_has=65, for_user=65)
        CreateFixtures.add_has_permission(14, 1110, rlc_has=91, for_rlc=92)
        CreateFixtures.add_has_permission(15, 1130, user_has=64, for_rlc=91)
        CreateFixtures.add_has_permission(16, 1130, group_has=72, for_rlc=91)

    @staticmethod
    def checkArrays(testRef, real, toGet):
        testRef.assertEqual(real.__len__(), toGet.__len__())
        for item in toGet:
            testRef.assertIn(item, real)

    def test_create_new_user_success(self):
        client = APIClient()
        before = UserProfile.objects.count()
        rlc = Rlc(name='rlc1')
        rlc.save()
        response = client.post(self.base_url_create, {
            "email": "peter_parker@gmx.to",
            'name': 'Peter Parker',
            'password': 'abc123',
            'rlc': rlc.id
        })
        after = UserProfile.objects.count()
        self.assertTrue(response.status_code == 201)
        self.assertTrue(before + 1 == after)

    def test_create_new_user_full_success(self):
        client = APIClient()
        before = UserProfile.objects.count()
        rlc = Rlc(name='rlc1')
        rlc.save()
        user = {
            'email': 'peter_parker@gmx.de',
            'name': 'Peter Parker',
            'birthday': '1990-12-4',
            'password': 'abc123',
            'phone_number': '1283812812',
            'street': 'Klausweg 12',
            'city': 'munich',
            'postal_code': '12321',
            'rlc': rlc.id
        }
        response = client.post(self.base_url_create, user)
        after = UserProfile.objects.count()
        self.assertTrue(response.status_code == 201)
        self.assertTrue(before + 1 == after)

    def test_create_new_user_error_no_email(self):
        client = APIClient()
        before = UserProfile.objects.count()
        response = client.post(self.base_url_create, {
            'name': 'Peter Parker',
            'password': 'abc123'
        })
        after = UserProfile.objects.count()
        self.assertTrue(response.status_code == 400)
        self.assertTrue(before == after)

    def test_create_new_user_error_wrong_email(self):
        client = APIClient()
        before = UserProfile.objects.count()
        response = client.post(self.base_url_create, {
            'email': 'peter_parker@.de',
            'name': 'Peter Parker',
            'password': 'abc123'
        })
        after = UserProfile.objects.count()
        self.assertTrue(response.status_code == 400)
        self.assertTrue(before == after)

    def test_create_new_user_error_no_name(self):
        client = APIClient()
        before = UserProfile.objects.count()
        response = client.post(self.base_url_create, {
            'email': 'peter_parker@gmx.de',
            'password': 'abc123'
        })
        after = UserProfile.objects.count()
        self.assertTrue(response.status_code == 400)
        self.assertTrue(before == after)

    def test_create_new_user_error_no_password(self):
        client = APIClient()
        before = UserProfile.objects.count()
        response = client.post(self.base_url_create, {
            'email': 'peter_parker@gmx.de',
            'name': 'Peter Parker',
        })
        after = UserProfile.objects.count()
        self.assertTrue(response.status_code == 400)
        self.assertTrue(before == after)

    def test_create_new_user_error_double_email(self):
        client = APIClient()
        client.post(self.base_url_create, {
            'email': 'peter_parker@gmx.de',
            'name': 'Peter Parker',
            'password': 'abc123'
        })
        before = UserProfile.objects.count()
        response = client.post(self.base_url_create, {
            'email': 'peter_parker@gmx.de',
            'name': 'Smithy',
            'password': 'xxx'
        })
        after = UserProfile.objects.count()
        self.assertTrue(response.status_code == 400)
        self.assertTrue(before == after)

    def test_show_all_profiles_error_unauthenticated(self):
        client = APIClient()
        response = client.get(self.base_url_profile)
        self.assertTrue(response.status_code == 401)

    def test_create_multiple_users_success(self):
        created = CreateFixtures.create_sample_users()
        after = UserProfile.objects.count()
        self.assertTrue(after == created.__len__())

    def test_show_all_profiles_success(self):
        response = self.client.get(self.base_url_profile)
        number_of_users = UserProfile.objects.count()
        self.assertTrue(response.status_code == 200)
        self.assertTrue(number_of_users == response.data.__len__())

    def test_edit_patch_own_profile_success(self):
        response = self.client.patch(self.base_url_profile + '{}/'.format(self.user.id), {
            'name': 'this is a test'
        })
        user_from_db = list(UserProfile.objects.filter(id=self.user.id))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(user_from_db.__len__() == 1)
        self.assertTrue(user_from_db[0].name == 'this is a test')

    def test_edit_patch_own_profile_success_postal_code(self):
        response = self.client.patch(self.base_url_profile + '{}/'.format(self.user.id), {
            'postal_code': '151515'
        })
        user_from_db = list(UserProfile.objects.filter(id=self.user.id))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(user_from_db.__len__() == 1)
        self.assertTrue(user_from_db[0].postal_code == '151515')

    def test_edit_patch_own_profile_error_no_name(self):
        user_from_db_before = list(UserProfile.objects.filter(id=self.user.id))
        response = self.client.patch(self.base_url_profile + '{}/'.format(self.user.id), {
            'name': ''
        })
        user_from_db_after = list(UserProfile.objects.filter(id=self.user.id))
        self.assertTrue(response.status_code == 400)
        self.assertEqual(user_from_db_after[0].name, user_from_db_before[0].name)

    def test_edit_patch_own_profile_wrong_email(self):
        user_from_db_before = list(UserProfile.objects.filter(id=self.user.id))
        response = self.client.patch(self.base_url_profile + '{}/'.format(self.user.id), {
            'email': 'blubl@.'
        })
        user_from_db_after = list(UserProfile.objects.filter(id=self.user.id))
        self.assertTrue(response.status_code == 400)
        self.assertEqual(user_from_db_after[0].email, user_from_db_before[0].email)

    def test_edit_foreign_profile(self):
        CreateFixtures.create_sample_users()
        user = list(UserProfile.objects.exclude(is_superuser=True))[0]
        other_users = list(UserProfile.objects.exclude(id=user.id))
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.patch(self.base_url_profile + '{}/'.format(other_users[0].id), {
            'name': 'new name'
        })
        other_users_after = list(UserProfile.objects.exclude(id=user.id))
        self.assertTrue(response.status_code == 403)
        self.assertTrue(other_users, other_users_after)

    def test_get_auth_token_success(self):
        client = APIClient()
        response = client.post('/api/login/', {
            'username': 'test123@test.com',
            'password': 'test123'
        })
        tok = Token.objects.get(key=response.data['token'])
        self.assertEqual(response.data['token'], tok.key)
        self.assertEqual(response.data['user']['id'], tok.user.id)

    def test_get_as_user_permissions(self):
        self.fixtures_has_permissions()

        user1 = UserProfile.objects.get(pk=62)
        user1_perms = user1.__get_as_user_permissions()

        UsersTests.checkArrays(self, [i.id for i in user1_perms], [1, 9])

    def test_get_overall_permissions(self):
        self.fixtures_has_permissions()

        user1 = UserProfile.objects.get(pk=62)
        user1_perms = user1.get_all_user_permissions()
        ids = []
        for perm in user1_perms:
            ids.append(perm.id)

        UsersTests.checkArrays(self, [i.id for i in user1_perms], [1, 5, 9, 14, 16])

    def test_get_overall_special_permissions(self):
        self.fixtures_has_permissions()

        user1 = UserProfile.objects.get(pk=65)
        user1_perms = user1.get_overall_special_permissions(permission=1120)

        UsersTests.checkArrays(self, [i.id for i in user1_perms], [13, 12])

    def test_has_permission(self):
        self.fixtures_has_permissions()

        user1 = UserProfile.objects.get(pk=63)

        self.assertTrue(user1.has_permission(1031, for_user=62))
        self.assertTrue(user1.has_permission(1032, for_user=64))
        self.assertTrue(user1.has_permission(1032, for_user=64))
        self.assertTrue(user1.has_permission(1110, for_rlc=92))
        self.assertTrue(user1.has_permission(1040, for_user=64))
        self.assertTrue(not user1.has_permission(1030, for_user=63))
        self.assertTrue(not user1.has_permission(1031, for_user=63))

    def test_get_users_with_special_permissions(self):
        self.fixtures_has_permissions()

        consultants = Rlc.objects.first().get_consultants()
        self.assertTrue(list(consultants).__len__() == 3)
