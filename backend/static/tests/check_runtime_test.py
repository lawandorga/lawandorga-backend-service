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

import time
from django.test import TransactionTestCase
from backend.files.tests.folder_model_test import FolderModelTests
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.files.models import Folder


class CheckRuntimeTest(TransactionTestCase):
    def setUp(self):
        self.fixtures = CreateFixtures.create_base_fixtures()

    def test_runtime(self):
        time_sum = 0

        for i in range(20):
            start_time = time.time()
            # replace below
            top_folder = Folder(
                name="top folder",
                creator=self.fixtures["users"][0]["user"],
                rlc=self.fixtures["rlc"],
            )
            top_folder.save()
            self.assertEqual(0, top_folder.get_all_parents().__len__())

            middle_folder = Folder(
                name="middle folder",
                creator=self.fixtures["users"][0]["user"],
                rlc=self.fixtures["rlc"],
                parent=top_folder,
            )
            middle_folder.save()
            parents = middle_folder.get_all_parents()
            self.assertEqual(1, parents.__len__())
            self.assertEqual(0, parents.index(top_folder))

            bottom_folder = Folder(
                name="bottom folder",
                creator=self.fixtures["users"][0]["user"],
                rlc=self.fixtures["rlc"],
                parent=middle_folder,
            )
            bottom_folder.save()
            parents = bottom_folder.get_all_parents()
            self.assertEqual(2, parents.__len__())
            self.assertEqual(0, parents.index(top_folder))
            self.assertEqual(1, parents.index(middle_folder))

            most_bottom = Folder(
                name="most bottom folder",
                creator=self.fixtures["users"][0]["user"],
                rlc=self.fixtures["rlc"],
                parent=bottom_folder,
            )
            most_bottom.save()
            parents = most_bottom.get_all_parents()
            self.assertEqual(3, parents.__len__())
            self.assertEqual(0, parents.index(top_folder))
            self.assertEqual(1, parents.index(middle_folder))
            self.assertEqual(2, parents.index(bottom_folder))

            most_bottom2 = Folder(
                name="most bottom 2 folder",
                creator=self.fixtures["users"][0]["user"],
                rlc=self.fixtures["rlc"],
                parent=bottom_folder,
            )
            most_bottom2.save()
            parents = most_bottom2.get_all_parents()
            self.assertEqual(3, parents.__len__())
            self.assertEqual(0, parents.index(top_folder))
            self.assertEqual(1, parents.index(middle_folder))
            self.assertEqual(2, parents.index(bottom_folder))

            Folder.objects.all().delete()
            # end replace
            time_sum = time_sum + (time.time() - start_time)

        print("average: ", time_sum / 20)
