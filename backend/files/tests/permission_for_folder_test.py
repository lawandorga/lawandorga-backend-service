#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2020  Dominik Walser
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
from backend.files.models import Folder, FolderPermission, PermissionForFolder


class PermissionForFolderTest(TransactionTestCase):
    def setUp(self):
        self.fixtures = CreateFixtures.create_base_fixtures()

    def test_create_same_permission_twice(self):
        permission = FolderPermission(name="read")
        permission.save()
        folder = Folder(
            name="folder1",
            size="123",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
        )
        folder.save()

        perm1 = PermissionForFolder(
            permission=permission,
            group_has_permission=self.fixtures["groups"][0],
            folder=folder,
        )
        perm1.save()
        self.assertEqual(1, PermissionForFolder.objects.count())

        # creating same
        perm2 = PermissionForFolder(
            permission=permission,
            group_has_permission=self.fixtures["groups"][0],
            folder=folder,
        )
        perm2.save()
        self.assertEqual(1, PermissionForFolder.objects.count())

        # creating different but changing afterwards
        perm3 = PermissionForFolder(
            permission=permission,
            group_has_permission=self.fixtures["groups"][1],
            folder=folder,
        )
        perm3.save()
        self.assertEqual(2, PermissionForFolder.objects.count())

        perm3.group_has_permission = self.fixtures["groups"][0]
        with self.assertRaises(Exception, msg="saving should fail and throw error"):
            perm3.save()
        self.assertEqual(1, PermissionForFolder.objects.count())

    def test_create_different_permission_group(self):
        permission = FolderPermission(name="read")
        permission.save()
        top_folder = Folder(
            name="top folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
        )
        top_folder.save()
        middle_folder = Folder(
            name="middle folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=top_folder,
        )
        middle_folder.save()

        perm1 = PermissionForFolder(
            permission=permission,
            group_has_permission=self.fixtures["groups"][0],
            folder=top_folder,
        )
        perm1.save()
        self.assertEqual(1, PermissionForFolder.objects.count())

        perm2 = PermissionForFolder(
            permission=permission,
            group_has_permission=self.fixtures["groups"][1],
            folder=middle_folder,
        )
        with self.assertRaises(Exception, msg="saving should fail"):
            perm2.save()
        self.assertEqual(1, PermissionForFolder.objects.count())

        perm3 = PermissionForFolder(
            permission=permission,
            group_has_permission=self.fixtures["groups"][1],
            folder=top_folder,
        )
        perm3.save()
        self.assertEqual(2, PermissionForFolder.objects.count())

        perm4 = PermissionForFolder(
            permission=permission,
            group_has_permission=self.fixtures["groups"][1],
            folder=middle_folder,
        )
        perm4.save()
        self.assertEqual(3, PermissionForFolder.objects.count())
