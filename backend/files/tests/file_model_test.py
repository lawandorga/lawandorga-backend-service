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
from backend.files.models import File, Folder
from backend.api.tests.fixtures_encryption import CreateFixtures


class FileModelTests(TransactionTestCase):
    def setUp(self):
        self.fixtures = CreateFixtures.create_base_fixtures()

    def test_delete_on_cloud(self):
        File.delete_on_cloud = MagicMock()
        folder = Folder(
            name="root folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
        )
        folder.save()
        folder2 = Folder(
            name="middle folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
        )
        folder2.save()
        file = File(
            name="file1",
            creator=self.fixtures["users"][0]["user"],
            folder=folder2,
            size=12,
        )
        file.save()
        file2 = File(
            name="file2",
            creator=self.fixtures["users"][0]["user"],
            folder=folder2,
            size=12,
        )
        file2.save()
        file3 = File(
            name="file3",
            creator=self.fixtures["users"][0]["user"],
            folder=folder,
            size=12,
        )
        file3.save()

        self.assertEqual(2, Folder.objects.count())
        self.assertEqual(3, File.objects.count())
        folder2.delete()
        self.assertEqual(1, Folder.objects.count())
        self.assertEqual(1, File.objects.count())
        self.assertEqual(2, File.delete_on_cloud.call_count)

    def test_update_folder_size(self):
        folder = Folder(
            name="root folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
        )
        folder.save()
        folder2 = Folder(
            name="middle folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=folder,
        )
        folder2.save()
        self.assertEqual(0, folder.size)
        self.assertEqual(0, folder2.size)

        file = File(
            name="file1",
            creator=self.fixtures["users"][0]["user"],
            folder=folder2,
            size=1000,
        )
        file.save()
        file2 = File(
            name="file2",
            creator=self.fixtures["users"][0]["user"],
            folder=folder,
            size=1000,
        )
        file2.save()
        self.assertEqual(2000, folder.size)
        self.assertEqual(1000, folder2.size)

        folder2.delete()
        self.assertEqual(1000, folder.size)
        self.assertEqual(1, File.objects.count())
        self.assertEqual(1, Folder.objects.count())
        self.assertEqual(1000, Folder.objects.first().size)

        file.delete()
        self.assertEqual(0, folder.size)

    def test_file_key(self):
        folder = Folder(
            name="root folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
        )
        folder.save()
        file = File(
            name="file1",
            creator=self.fixtures["users"][0]["user"],
            folder=folder,
            size=1000,
        )
        file.save()

        self.assertEqual("rlcs/3001/root folder/file1", file.get_file_key())

    def test_duplicate_file(self):
        folder = Folder(
            name="root folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
        )
        folder.save()
        file = File(
            name="file1",
            creator=self.fixtures["users"][0]["user"],
            folder=folder,
            size=1000,
        )
        File.create_or_update(file)

        file2 = File(
            name="file1",
            creator=self.fixtures["users"][0]["user"],
            folder=folder,
            size=1238,
        )
        File.create_or_update(file2)
        self.assertEqual(1, File.objects.count())
        self.assertEqual(1238, File.objects.get(name="file1", folder=folder).size)
