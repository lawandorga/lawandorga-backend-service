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

from unittest.mock import MagicMock

from django.test import TransactionTestCase
from backend.files.models import PermissionForFolder, FolderPermission, Folder
from backend.api.models import UserProfile, Rlc, Group
from backend.api.tests.fixtures_encryption import CreateFixtures


class PermissionForFolderTest(TransactionTestCase):
    def setUp(self):
        pass

    def test_create_same_permission_twice(self):
        permission = FolderPermission(name='read')
        permission.save()
        rlc = Rlc(name='testrlc')
        rlc.save()

        user = UserProfile(name='user1', rlc=rlc)
        user.save()
        folder = Folder(name='folder1', size='123', creator=user, rlc=rlc)
        folder.save()
        group = Group(name='group1', from_rlc=rlc)
        group.save()
        group2 = Group(name='group2', from_rlc=rlc)
        group2.save()

        perm1 = PermissionForFolder(permission=permission, group_has_permission=group, folder=folder)
        perm1.save()
        self.assertEqual(1, PermissionForFolder.objects.count())

        # creating same
        perm2 = PermissionForFolder(permission=permission, group_has_permission=group, folder=folder)
        perm2.save()
        self.assertEqual(1, PermissionForFolder.objects.count())

        # creating different but changing afterwards
        perm3 = PermissionForFolder(permission=permission, group_has_permission=group2, folder=folder)
        perm3.save()
        self.assertEqual(2, PermissionForFolder.objects.count())

        perm3.group_has_permission = group
        try:
            perm3.save()
            self.assertTrue(False)  # expected to throw error
        except Exception:
            pass
        self.assertEqual(1, PermissionForFolder.objects.count())

    def test_create_different_permission_group(self):
        pass
