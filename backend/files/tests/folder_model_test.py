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
from backend.files.models import Folder
from backend.api.tests.fixtures_encryption import CreateFixtures


class FolderModelTests(TransactionTestCase):
    def setUp(self):
        self.fixtures = CreateFixtures.create_fixtures()

    def test_delete_on_cloud_called(self):
        folder = Folder(name='folder1', creator=self.fixtures['users'][0]['user'], rlc=self.fixtures['rlc'])
        folder.delete_on_cloud = MagicMock(return_value=True)
        folder.save()
        self.assertEqual(Folder.objects.count(), 1)
        folder.delete()
        self.assertEqual(Folder.objects.count(), 0)
        folder.delete_on_cloud.assert_called_once()

    def test_delete_with_children(self):
        Folder.delete_on_cloud = MagicMock()

        parent_folder = Folder(name='parent_folder', creator=self.fixtures['users'][0]['user'],
                               rlc=self.fixtures['rlc'])
        parent_folder.save()

        children_folder = Folder(name="child", creator=self.fixtures['users'][0]['user'], rlc=self.fixtures['rlc'],
                                 parent=parent_folder)
        children_folder.save()

        self.assertEqual(Folder.objects.count(), 2)
        parent_folder.delete()
        self.assertEqual(Folder.objects.count(), 0)
        self.assertEqual(Folder.delete_on_cloud.call_count, 2)

    def test_delete_size_updating(self):
        top_folder = Folder(name='top folder', creator=self.fixtures['users'][0]['user'], rlc=self.fixtures['rlc'],
                            size=100)
        top_folder.save()
        middle_folder = Folder(name='middle folder', creator=self.fixtures['users'][0]['user'],
                               rlc=self.fixtures['rlc'], size=100, parent=top_folder)
        middle_folder.save()
        bottom_folder = Folder(name='bottom folder', creator=self.fixtures['users'][0]['user'],
                               rlc=self.fixtures['rlc'], size=60, parent=middle_folder)
        bottom_folder.save()

        self.assertEqual(Folder.objects.count(), 3)
        middle_folder.delete()
        self.assertEqual(Folder.objects.count(), 1)
        self.assertEqual(top_folder.size, 100)

    def test_add_size_updating(self):
        top_folder = Folder(name='top folder', creator=self.fixtures['users'][0]['user'], rlc=self.fixtures['rlc'])
        top_folder.save()
        self.assertEqual(top_folder.size, 0)

        middle_folder = Folder(name='middle folder', creator=self.fixtures['users'][0]['user'],
                               rlc=self.fixtures['rlc'], size=100, parent=top_folder)
        middle_folder.save()
        self.assertTrue(top_folder.size, 100)

        bottom_folder = Folder(name='bottom folder', creator=self.fixtures['users'][0]['user'],
                               rlc=self.fixtures['rlc'], size=60, parent=middle_folder)
        bottom_folder.save()
        self.assertEqual(top_folder.size, 160)

    def test_folder_key(self):
        top_folder = Folder(name='top folder', creator=self.fixtures['users'][0]['user'], rlc=self.fixtures['rlc'])
        top_folder.save()
        middle_folder = Folder(name='middle folder', creator=self.fixtures['users'][0]['user'],
                               rlc=self.fixtures['rlc'], parent=top_folder)
        middle_folder.save()
        bottom_folder = Folder(name='bottom folder', creator=self.fixtures['users'][0]['user'],
                               rlc=self.fixtures['rlc'], parent=middle_folder)
        bottom_folder.save()

        self.assertEqual('rlcs/1/files/top folder/middle folder/bottom folder/',
                         bottom_folder.get_file_key())
        self.assertEqual('rlcs/1/files/top folder/middle folder/',
                         middle_folder.get_file_key())
        self.assertEqual('rlcs/1/files/top folder/', top_folder.get_file_key())
