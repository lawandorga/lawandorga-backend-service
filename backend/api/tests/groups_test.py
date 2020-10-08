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
from rest_framework.test import APIClient
from rest_framework.response import Response

from backend.api.models import UserProfile, Group, HasPermission, Permission, Rlc
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.static.permissions import (
    PERMISSION_ADD_GROUP_RLC,
    PERMISSION_MANAGE_GROUPS_RLC,
)


class GroupsTests(TransactionTestCase):
    def setUp(self):
        self.base_fixtures = CreateFixtures.create_base_fixtures()
        self.base_url: str = "/api/groups/"
        self.client: APIClient = self.base_fixtures["users"][0]["client"]
        self.user: UserProfile = self.base_fixtures["users"][0]["user"]
        self.private_key: bytes = self.base_fixtures["users"][0]["private"]

    def test_has_group_permission(self):
        perm1 = Permission(name="test_permission_1")
        perm1.save()
        perm2 = Permission(name="test_permission_2")
        perm2.save()
        rlc = Rlc(name="test rlc1")
        rlc.save()
        group = Group(from_rlc=rlc, name="test group 1", visible=True)
        group.save()

        hasperm1 = HasPermission(
            group_has_permission=group, permission=perm1, permission_for_rlc=rlc
        )
        hasperm1.save()
        self.assertTrue(group.has_group_permission(perm1))
        self.assertTrue(group.has_group_permission(perm1.name))

    def test_has_group_one_permission(self):
        perm1 = Permission(name="test_permission_1")
        perm1.save()
        perm2 = Permission(name="test_permission_2")
        perm2.save()
        rlc = Rlc(name="test rlc1")
        rlc.save()
        group = Group(from_rlc=rlc, name="test group 1", visible=True)
        group.save()

        hasperm1 = HasPermission(
            group_has_permission=group, permission=perm1, permission_for_rlc=rlc
        )
        hasperm1.save()
        self.assertTrue(group.has_group_one_permission([perm1, perm2]))

    def test_has_group_one_permission_2(self):
        perm1 = Permission(name="test_permission_1")
        perm1.save()
        perm2 = Permission(name="test_permission_2")
        perm2.save()
        rlc = Rlc(name="test rlc1")
        rlc.save()
        group = Group(from_rlc=rlc, name="test group 1", visible=True)
        group.save()

        hasperm1 = HasPermission(
            group_has_permission=group, permission=perm1, permission_for_rlc=rlc
        )
        hasperm1.save()
        self.assertTrue(not group.has_group_one_permission([perm2]))

    def test_create_group_success(self):
        has_permission = CreateFixtures.add_permission_for_user(
            user=self.user, permission=PERMISSION_ADD_GROUP_RLC
        )

        # with add group permission
        number_of_groups_before = Group.objects.count()
        response: Response = self.client.post(
            self.base_url, {"name": "the best new group", "visible": True}
        )
        self.assertEqual(201, response.status_code)
        self.assertEquals(number_of_groups_before + 1, Group.objects.count())

        # without name
        number_of_groups_before = Group.objects.count()
        response: Response = self.client.post(self.base_url, {"visible": True})
        self.assertEqual(400, response.status_code)
        self.assertEquals(number_of_groups_before, Group.objects.count())

        # without visible
        response: Response = self.client.post(
            self.base_url, {"name": "the best new group"}
        )
        self.assertEqual(400, response.status_code)
        self.assertEquals(number_of_groups_before, Group.objects.count())

        # without permissions
        has_permission.delete()
        response: Response = self.client.post(
            self.base_url, {"name": "the best new group", "visible": True}
        )

        self.assertEqual(403, response.status_code)
        self.assertEquals(number_of_groups_before, Group.objects.count())

        CreateFixtures.add_permission_for_user(self.user, PERMISSION_MANAGE_GROUPS_RLC)

        # with manage groups permission
        response: Response = self.client.post(
            self.base_url, {"name": "the second best new group", "visible": True}
        )
        self.assertEqual(201, response.status_code)
        self.assertEquals(number_of_groups_before + 1, Group.objects.count())

        # double name in rlc
        number_of_groups_before = Group.objects.count()
        response: Response = self.client.post(
            self.base_url, {"name": "the second best new group", "visible": True}
        )
        self.assertEqual(400, response.status_code)
        self.assertEquals(number_of_groups_before, Group.objects.count())

    def test_add_group_member(self):
        group: Group = self.base_fixtures["groups"][0]
        user3: UserProfile = self.base_fixtures["users"][2]["user"]
        user4: UserProfile = self.base_fixtures["users"][3]["user"]
        group_member_url = "/api/group_members/"

        number_of_group_members: int = group.group_members.count()

        response: Response = self.client.post(
            group_member_url,
            {"action": "remove"},
            **{"HTTP_PRIVATE_KEY": self.private_key}
        )
        self.assertEqual(403, response.status_code)

        CreateFixtures.add_permission_for_user(self.user, PERMISSION_MANAGE_GROUPS_RLC)

        response: Response = self.client.post(
            group_member_url,
            {"action": "remove"},
            **{"HTTP_PRIVATE_KEY": self.private_key}
        )
        self.assertEqual(400, response.status_code)

        response: Response = self.client.post(
            group_member_url,
            {"action": "remove", "group_id": group.id},
            **{"HTTP_PRIVATE_KEY": self.private_key}
        )
        self.assertEqual(400, response.status_code)

        response: Response = self.client.post(
            group_member_url,
            {"action": "add", "group_id": group.id, "user_ids": [user3.id, user4.id]},
            format="json",
            **{"HTTP_PRIVATE_KEY": self.private_key}
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(number_of_group_members + 2, group.group_members.count())

        response: Response = self.client.post(
            group_member_url,
            {
                "action": "remove",
                "group_id": group.id,
                "user_ids": [user3.id, user4.id],
            },
            format="json",
            **{"HTTP_PRIVATE_KEY": self.private_key}
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(number_of_group_members, group.group_members.count())

        # TODO: doubled add

        # if 'action' not in request.data or 'group_id' not in request.data or 'user_ids' not in request.data:
