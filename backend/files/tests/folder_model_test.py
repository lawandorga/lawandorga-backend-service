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

from backend.api.models import HasPermission, Permission
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.files.models import File, Folder, FolderPermission, PermissionForFolder
from backend.files.static.folder_permissions import PERMISSION_READ_FOLDER
from backend.static.permissions import PERMISSION_READ_ALL_FOLDERS_RLC


class FolderModelTests(TransactionTestCase):
    def setUp(self):
        self.fixtures = CreateFixtures.create_base_fixtures()

    def test_delete_on_cloud_called(self):
        folder = Folder(
            name="folder1",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
        )
        folder.delete_on_cloud = MagicMock(return_value=True)
        folder.save()
        self.assertEqual(Folder.objects.count(), 1)
        folder.delete()
        self.assertEqual(Folder.objects.count(), 0)
        folder.delete_on_cloud.assert_called_once()

    def test_delete_with_children(self):
        Folder.delete_on_cloud = MagicMock()

        parent_folder = Folder(
            name="parent_folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
        )
        parent_folder.save()

        children_folder = Folder(
            name="child",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=parent_folder,
        )
        children_folder.save()

        self.assertEqual(Folder.objects.count(), 2)
        parent_folder.delete()
        self.assertEqual(Folder.objects.count(), 0)
        self.assertEqual(Folder.delete_on_cloud.call_count, 2)

    def test_delete_size_updating(self):
        top_folder = Folder(
            name="top folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            size=100,
        )
        top_folder.save()
        middle_folder = Folder(
            name="middle folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            size=100,
            parent=top_folder,
        )
        middle_folder.save()
        middle_folder.update_folder_tree_sizes(middle_folder.size)
        self.assertEqual(200, top_folder.size)
        bottom_folder = Folder(
            name="bottom folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            size=60,
            parent=middle_folder,
        )
        bottom_folder.save()
        bottom_folder.update_folder_tree_sizes(bottom_folder.size)
        self.assertEqual(260, top_folder.size)
        self.assertEqual(160, middle_folder.size)
        self.assertEqual(Folder.objects.count(), 3)

        middle_folder.delete()
        self.assertEqual(Folder.objects.count(), 1)
        self.assertEqual(top_folder.size, 100)

    def test_add_size_updating(self):
        top_folder = Folder(
            name="top folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
        )
        top_folder.save()
        self.assertEqual(top_folder.size, 0)

        middle_folder = Folder(
            name="middle folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            size=100,
            parent=top_folder,
        )
        middle_folder.save()
        middle_folder.update_folder_tree_sizes(100)
        self.assertTrue(top_folder.size, 100)

        bottom_folder = Folder(
            name="bottom folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            size=60,
            parent=middle_folder,
        )
        bottom_folder.save()
        bottom_folder.propagate_new_size_up(60)
        self.assertEqual(top_folder.size, 160)
        self.assertEqual(middle_folder.size, 160)
        middle_folder.name = "middle folder new"
        middle_folder.save()
        self.assertEqual(top_folder.size, 160)
        self.assertEqual(Folder.objects.get(name="middle folder new").size, 160)
        self.assertEqual(160, Folder.objects.get(name="top folder").size)
        middle_folder.size = 200
        middle_folder.update_folder_tree_sizes(40)
        self.assertEqual(200, middle_folder.size)
        self.assertEqual(200, top_folder.size)
        self.assertEqual(200, Folder.objects.get(name="middle folder new").size)
        self.assertEqual(200, Folder.objects.get(name="top folder").size)

    def test_size_updating_with_files(self):
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
        self.assertEqual(top_folder.size, 0)
        self.assertEqual(middle_folder.size, 0)

        file1 = File(
            name="file1",
            size=100,
            creator=self.fixtures["users"][0]["user"],
            folder=top_folder,
        )
        file1.save()
        self.assertEqual(top_folder.size, 100)
        self.assertEqual(middle_folder.size, 0)

        file2 = File(
            name="file2",
            size=200,
            creator=self.fixtures["users"][0]["user"],
            folder=middle_folder,
        )
        file2.save()
        self.assertEqual(top_folder.size, 300)
        self.assertEqual(middle_folder.size, 200)

        bottom_folder = Folder(
            name="bottom folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=middle_folder,
        )
        bottom_folder.save()
        self.assertEqual(top_folder.size, 300)
        self.assertEqual(middle_folder.size, 200)
        self.assertEqual(bottom_folder.size, 0)

        file3 = File(
            name="file3",
            size=200,
            creator=self.fixtures["users"][0]["user"],
            folder=bottom_folder,
        )
        file3.save()
        self.assertEqual(top_folder.size, 500)
        self.assertEqual(middle_folder.size, 400)
        self.assertEqual(bottom_folder.size, 200)

        bottom_folder.delete()
        self.assertEqual(top_folder.size, 300)
        self.assertEqual(middle_folder.size, 200)

    def test_folder_key(self):
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
        bottom_folder = Folder(
            name="bottom folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=middle_folder,
        )
        bottom_folder.save()

        self.assertEqual(
            "rlcs/3001/top folder/middle folder/bottom folder/",
            bottom_folder.get_file_key(),
        )
        self.assertEqual(
            "rlcs/3001/top folder/middle folder/", middle_folder.get_file_key()
        )
        self.assertEqual("rlcs/3001/top folder/", top_folder.get_file_key())

    def test_folder_tree(self):
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

    def test_get_folder_from_path(self):
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
        bottom_folder = Folder(
            name="bottom folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=middle_folder,
        )
        bottom_folder.save()

        self.assertEqual(
            bottom_folder,
            Folder.get_folder_from_path(
                "top folder/middle folder/bottom folder/", self.fixtures["rlc"]
            ),
        )
        self.assertEqual(
            bottom_folder,
            Folder.get_folder_from_path(
                "top folder/middle folder/bottom folder", self.fixtures["rlc"]
            ),
        )
        self.assertEqual(
            bottom_folder,
            Folder.get_folder_from_path(
                "top folder/middle folder/bottom folder/asd.pdf", self.fixtures["rlc"]
            ),
        )

    def test_folder_no_duplicated_names(self):
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

        middle_folder2 = Folder(
            name="middle folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=top_folder,
        )
        with self.assertRaises(Exception, msg="saving should fail"):
            middle_folder2.save()
        self.assertEqual(2, Folder.objects.count())

    def test_user_has_permission(self):
        p_read = FolderPermission.objects.get(name=PERMISSION_READ_FOLDER)
        p_all_read = Permission.objects.get(name=PERMISSION_READ_ALL_FOLDERS_RLC)
        overall_read = HasPermission(
            permission=p_all_read,
            user_has_permission=self.fixtures["users"][3]["user"],

        )
        overall_read.save()
        created_folders = self.create_many_test_folders()

        self.assertFalse(
            created_folders["ressorts"].user_has_permission_read(
                self.fixtures["users"][0]["user"]
            )
        )
        self.assertFalse(
            created_folders["ressorts"].user_can_see_folder(
                self.fixtures["users"][0]["user"]
            )
        )

        perm1 = PermissionForFolder(
            folder=created_folders["ressorts"],
            permission=p_read,
            group_has_permission=self.fixtures["groups"][0],
        )
        perm1.save()

        self.assertTrue(
            created_folders["ressorts"].user_has_permission_read(
                self.fixtures["users"][0]["user"]
            )
        )
        self.assertTrue(
            created_folders["public"].user_has_permission_read(
                self.fixtures["users"][0]["user"]
            )
        )
        self.assertTrue(
            created_folders["post_date"].user_has_permission_read(
                self.fixtures["users"][0]["user"]
            )
        )
        self.assertFalse(
            created_folders["ressorts"].user_has_permission_read(
                self.fixtures["users"][2]["user"]
            )
        )
        self.assertFalse(
            created_folders["ressorts"].user_can_see_folder(
                self.fixtures["users"][2]["user"]
            )
        )

        perm2 = PermissionForFolder(
            folder=created_folders["instagram"],
            permission=p_read,
            group_has_permission=self.fixtures["groups"][1],
        )
        perm2.save()

        self.assertTrue(
            created_folders["ressorts"].user_can_see_folder(
                self.fixtures["users"][2]["user"]
            )
        )
        self.assertTrue(
            created_folders["public"].user_can_see_folder(
                self.fixtures["users"][2]["user"]
            )
        )
        self.assertFalse(
            created_folders["ressorts"].user_has_permission_read(
                self.fixtures["users"][2]["user"]
            )
        )
        self.assertTrue(
            created_folders["instagram"].user_has_permission_read(
                self.fixtures["users"][2]["user"]
            )
        )
        self.assertTrue(
            created_folders["posts"].user_has_permission_read(
                self.fixtures["users"][2]["user"]
            )
        )

    def test_get_groups_permission(self):
        p_read = FolderPermission.objects.get(name=PERMISSION_READ_FOLDER)
        p_all_read = Permission.objects.get(name=PERMISSION_READ_ALL_FOLDERS_RLC)

        created_folders = self.create_many_test_folders()

        perm1 = PermissionForFolder(
            folder=created_folders["ressorts"],
            permission=p_read,
            group_has_permission=self.fixtures["groups"][0],
        )
        perm1.save()

        perm_string, perm = created_folders["ressorts"].get_groups_permission(
            self.fixtures["groups"][0]
        )
        self.assertEquals("READ", perm_string)
        self.assertEquals(perm1, perm)
        perm_string, perm = created_folders["ressorts"].get_groups_permission(
            self.fixtures["groups"][1]
        )
        self.assertEquals("", perm_string)

        perm2 = PermissionForFolder(
            folder=created_folders["instagram"],
            permission=p_read,
            group_has_permission=self.fixtures["groups"][1],
        )
        perm2.save()

        perm_string, perm = created_folders["ressorts"].get_groups_permission(
            self.fixtures["groups"][1]
        )
        self.assertEquals("SEE", perm_string)
        self.assertEquals(perm2, perm)
        perm_string, perm = created_folders["instagram"].get_groups_permission(
            self.fixtures["groups"][1]
        )
        self.assertEquals("READ", perm_string)
        self.assertEquals(perm2, perm)
        perm_string, perm = created_folders["instagram"].get_groups_permission(
            self.fixtures["groups"][0]
        )
        self.assertEquals("READ", perm_string)

    def test_get_all_groups_permissions_new(self):
        p_read = FolderPermission.objects.get(name=PERMISSION_READ_FOLDER)
        p_all_read = Permission.objects.get(name=PERMISSION_READ_ALL_FOLDERS_RLC)

        created_folders = self.create_many_test_folders()

        perm1 = PermissionForFolder(
            folder=created_folders["ressorts"],
            permission=p_read,
            group_has_permission=self.fixtures["groups"][0],
        )
        perm1.save()

        perms = created_folders["ressorts"].get_all_groups_permissions()

    # def test_download_folder(self):
    #   TODO: this?
    #
    #     top_folder = Folder(name='files', creator=self.fixtures['users'][0]['user'], rlc=self.fixtures['rlc'])
    #     top_folder.save()
    #     middle_folder = Folder(name='middle folder', creator=self.fixtures['users'][0]['user'],
    #                            rlc=self.fixtures['rlc'], parent=top_folder)
    #     middle_folder.save()
    #     file1 = File(name='')

    def test_download_real(self):
        top_folder = Folder(
            name="ressorts",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
        )
        top_folder.save()
        file = File(
            name="pf1.pdf",
            creator=self.fixtures["users"][0]["user"],
            size=93119,
            folder=top_folder,
        )
        file.save()
        file2 = File(
            name="pf2.pdf",
            creator=self.fixtures["users"][0]["user"],
            size=83796,
            folder=top_folder,
        )
        file2.save()
        middle_folder = Folder(
            name="beirat",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=top_folder,
        )
        middle_folder.save()
        file3 = File(
            name="pinguin1.pdf",
            creator=self.fixtures["users"][0]["user"],
            size=83796,
            folder=middle_folder,
        )
        file3.save()

        top_folder.download_folder()
        self.assertTrue(True)

        from backend.static.storage_management import LocalStorageManager

        LocalStorageManager.zip_folder_and_delete("temp/ressorts", "temp/ressorts")

    def test_create_folders_for_file_path(self):
        top_folder = Folder(
            name="ressorts",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
        )
        top_folder.save()
        self.assertEqual(1, Folder.objects.count())

        path = "mitglieder/ausbildung/asdsd.pdf"
        Folder.create_folders_for_file_path(
            top_folder, path, self.fixtures["users"][0]["user"]
        )
        self.assertEqual(3, Folder.objects.count())

        path = "mitglieder/alumni/askdks.pdf"
        Folder.create_folders_for_file_path(
            top_folder, path, self.fixtures["users"][0]["user"]
        )
        self.assertEqual(4, Folder.objects.count())

        path = "mitglieder/alumni/aakdks.pdf"
        Folder.create_folders_for_file_path(
            top_folder, path, self.fixtures["users"][0]["user"]
        )
        self.assertEqual(4, Folder.objects.count())

    def create_many_test_folders(self):
        created_folders = {}
        folder_ressorts = Folder(
            name="Ressorts",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
        )
        folder_ressorts.save()
        created_folders.update({"ressorts": folder_ressorts})

        folder_public = Folder(
            name="Oeffentlichkeitsarbeit",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=folder_ressorts,
        )
        folder_public.save()
        created_folders.update({"public": folder_public})

        folder_social = Folder(
            name="Social media",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=folder_public,
        )
        folder_social.save()
        created_folders.update({"social": folder_social})

        folder_instagram = Folder(
            name="Instagram",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=folder_social,
        )
        folder_instagram.save()
        created_folders.update({"instagram": folder_instagram})

        folder_posts = Folder(
            name="Posts",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=folder_instagram,
        )
        folder_posts.save()
        created_folders.update({"posts": folder_posts})

        folder_post_date = Folder(
            name="24.12.2014",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=folder_posts,
        )
        folder_post_date.save()
        created_folders.update({"post_date": folder_post_date})

        folder_stories = Folder(
            name="Stories",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=folder_instagram,
        )
        folder_stories.save()
        created_folders.update({"stories": folder_stories})

        folder_facebook = Folder(
            name="Facebook",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=folder_social,
        )
        folder_facebook.save()
        created_folders.update({"facebook": folder_facebook})

        folder_fundraising = Folder(
            name="Fundraising",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=folder_ressorts,
        )
        folder_fundraising.save()
        created_folders.update({"fundraising": folder_fundraising})

        folder_template = Folder(
            name="Vorlagen",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
        )
        folder_template.save()
        created_folders.update({"template": folder_template})

        return created_folders

    def test_get_all_parents(self):
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
        middle_folder_2 = Folder(
            name="middle folder 2",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=top_folder,
        )
        middle_folder_2.save()
        bottom_folder = Folder(
            name="bottom folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=middle_folder,
        )
        bottom_folder.save()

        self.assertEquals([], top_folder.get_all_parents())
        self.assertEquals([top_folder], middle_folder.get_all_parents())
        self.assertEquals([top_folder], middle_folder_2.get_all_parents())
        self.assertEquals([top_folder, middle_folder], bottom_folder.get_all_parents())

    def test_get_all_children(self):
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
        middle_folder_2 = Folder(
            name="middle folder 2",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=top_folder,
        )
        middle_folder_2.save()
        bottom_folder = Folder(
            name="bottom folder",
            creator=self.fixtures["users"][0]["user"],
            rlc=self.fixtures["rlc"],
            parent=middle_folder,
        )
        bottom_folder.save()

        self.assertEquals([], bottom_folder.get_all_children())
        self.assertEquals([bottom_folder], middle_folder.get_all_children())
        self.assertEquals([], middle_folder_2.get_all_children())
        self.assertCountEqual(
            [middle_folder_2, middle_folder, bottom_folder],
            top_folder.get_all_children(),
        )
