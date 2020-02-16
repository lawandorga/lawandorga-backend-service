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
from backend.files.models import File, Folder, FolderPermission, PermissionForFolder
from backend.files.static.folder_permissions import PERMISSION_READ_FOLDER
from backend.api.models import Permission, HasPermission
from backend.static.permissions import PERMISSION_ACCESS_TO_FILES_RLC


class FolderViewsTest(TransactionTestCase):
    def setUp(self):
        self.fixtures = CreateFixtures.create_base_fixtures()

        root_folder = Folder(name='files', creator=self.fixtures['users'][0]['user'],
                             rlc=self.fixtures['rlc'])
        root_folder.save()
        self.root_folder = root_folder
        middle_folder = Folder(name='ressorts', creator=self.fixtures['users'][0]['user'],
                               rlc=self.fixtures['rlc'], parent=root_folder)
        middle_folder.save()
        file = File(name='test file', creator=self.fixtures['users'][0]['user'], size=1000, folder=root_folder)
        file.save()

    def test_get_folder_information(self):
        response = self.fixtures['users'][0]['client'].get('/api/files/folder')
        self.assertEqual(200, response.status_code)
        self.assertTrue('files' in response.data)
        self.assertTrue('folders' in response.data)
        self.assertEqual(1, response.data['folders'].__len__())
        self.assertTrue(response.data['folders'][0]['name'] == 'ressorts')
        self.assertEqual(1, response.data['files'].__len__())

        middle_folder_2 = Folder(name='vorlagen', creator=self.fixtures['users'][0]['user'],
                                 rlc=self.fixtures['rlc'], parent=self.root_folder)
        middle_folder_2.save()

        response = self.fixtures['users'][0]['client'].get('/api/files/folder')
        self.assertEqual(2, response.data['folders'].__len__())

        folder_permission = FolderPermission.objects.get(name=PERMISSION_READ_FOLDER)
        permission_for_folder = PermissionForFolder(permission=folder_permission, folder=middle_folder_2,
                                                    group_has_permission=self.fixtures['groups'][1])
        permission_for_folder.save()
        response = self.fixtures['users'][0]['client'].get('/api/files/folder')
        self.assertEqual(1, response.data['folders'].__len__())

    def test_get_download_folder(self):
        response = self.fixtures['users'][0]['client'].get('/api/files/folder_download')
        self.assertEqual(400, response.status_code)

        access = Permission.objects.get(name=PERMISSION_ACCESS_TO_FILES_RLC)
        has_permission = HasPermission(permission=access, group_has_permission=self.fixtures['groups'][0], permission_for_rlc=self.fixtures['rlc'])
        has_permission.save()

        response = self.fixtures['users'][0]['client'].get('/api/files/folder_download')
        self.assertEqual(200, response.status_code)

        a = 10
