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

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TransactionTestCase
from unittest.mock import MagicMock, patch

from backend.static.storage_management import LocalStorageManager
from backend.static.storage_folders import get_temp_storage_path


class LocalStorageManagerTests(TransactionTestCase):
    def setUp(self) -> None:
        pass

    def test_save_locally(self):
        f = open('given_test_files/localStorageSaveTest/7_1_19__pass.jpg', 'rb')
        files = InMemoryUploadedFile(f, 'files', '7_1_19__pass.jpg', 'image/jpeg', 18839, None)
        with patch(get_temp_storage_path) as temp_storage_path:
            temp_storage_path.return_value = 'aaa/'
            LocalStorageManager.save_files_locally(files)
        f.close()


