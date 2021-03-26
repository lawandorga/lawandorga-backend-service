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
from rest_framework.response import Response
from rest_framework.test import APIClient

from backend.api.errors import CustomError
from backend.api.models import Group, HasPermission, Permission
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.collab.models import (
    CollabDocument,
    CollabPermission,
    PermissionForCollabDocument,
    TextDocument,
)
from backend.collab.static.collab_permissions import (
    PERMISSION_READ_DOCUMENT,
    PERMISSION_WRITE_DOCUMENT,
)
from backend.static.permissions import (
    PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC,
    PERMISSION_MANAGE_GROUPS_RLC,
    PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC,
)


class CollabDocumentModelTest(TransactionTestCase):
    def setUp(self) -> None:
        self.base_fixtures = CreateFixtures.create_base_fixtures()

    def test_create(self):
        document = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="test doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        self.assertEqual(1, CollabDocument.objects.count())
        self.assertEqual(1, TextDocument.objects.count())
        self.assertEqual("test doc 1", document.path)

    def test_name_with_slash_value_error(self):
        with self.assertRaises(CustomError):
            CollabDocument.objects.create(
                rlc=self.base_fixtures["rlc"],
                path="test/doc 2",
                creator=self.base_fixtures["users"][0]["user"],
            )
        self.assertEqual(0, CollabDocument.objects.count())
        self.assertEqual(0, TextDocument.objects.count())

    def test_create_duplicates(self):
        create_data = {
            "rlc": self.base_fixtures["rlc"],
            "path": "test doc 1",
            "creator": self.base_fixtures["users"][0]["user"],
        }

        CollabDocument.objects.create(**create_data)
        self.assertEqual(1, CollabDocument.objects.count())

        document: CollabDocument = CollabDocument.objects.create(**create_data)
        self.assertEqual(2, CollabDocument.objects.count())
        self.assertEqual(2, TextDocument.objects.count())
        self.assertEqual(document.path, "{}(1)".format(create_data["path"]))

        document: CollabDocument = CollabDocument.objects.create(**create_data)
        self.assertEqual(3, CollabDocument.objects.count())
        self.assertEqual(3, TextDocument.objects.count())
        self.assertEqual(document.path, "{}(2)".format(create_data["path"]))

    def test_create_without_parent_value_error(self):
        with self.assertRaises(CustomError):
            CollabDocument.objects.create(
                rlc=self.base_fixtures["rlc"],
                path="first non existent level/test doc 2",
                creator=self.base_fixtures["users"][0]["user"],
            )
        self.assertEqual(0, CollabDocument.objects.count())
        self.assertEqual(0, TextDocument.objects.count())

    def test_user_can_see_document_false(self):
        document: CollabDocument = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="test doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        self.assertEqual(
            (False, False),
            document.user_can_see(self.base_fixtures["users"][0]["user"]),
        )

    def test_user_can_see_document_direct(self):
        document: CollabDocument = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="test doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        collab_permission, created = CollabPermission.objects.get_or_create(
            name=PERMISSION_WRITE_DOCUMENT
        )
        PermissionForCollabDocument.objects.create(
            document=document,
            permission=collab_permission,
            group_has_permission=self.base_fixtures["groups"][0],
        )
        self.assertEqual(
            (True, True), document.user_can_see(self.base_fixtures["users"][0]["user"])
        )

    def test_user_can_see_document_indirect(self):
        document: CollabDocument = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="test doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        document_middle: CollabDocument = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="{}/{}".format(document.path, "middle doc"),
            creator=self.base_fixtures["users"][0]["user"],
        )
        document_top: CollabDocument = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="test doc 2",
            creator=self.base_fixtures["users"][0]["user"],
        )

        collab_permission, created = CollabPermission.objects.get_or_create(
            name=PERMISSION_WRITE_DOCUMENT
        )
        PermissionForCollabDocument.objects.create(
            document=document_middle,
            permission=collab_permission,
            group_has_permission=self.base_fixtures["groups"][0],
        )
        self.assertEqual(
            (True, False),
            document.user_can_see(self.base_fixtures["users"][0]["user"]),
        )
        self.assertEqual(
            (True, True),
            document_middle.user_can_see(self.base_fixtures["users"][0]["user"]),
        )
        self.assertEqual(
            (False, False),
            document_top.user_can_see(self.base_fixtures["users"][0]["user"]),
        )

    def test_user_has_permission_read(self):
        user = self.base_fixtures["users"][0]["user"]
        document: CollabDocument = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"], path="test doc 1", creator=user,
        )
        self.assertTrue(CollabDocument.user_has_permission_read(document.path, user))

        document_middle: CollabDocument = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="{}/{}".format(document.path, "middle doc"),
            creator=self.base_fixtures["users"][0]["user"],
        )
        self.assertFalse(
            CollabDocument.user_has_permission_read(document_middle.path, user)
        )

        collab_permission_read, created = CollabPermission.objects.get_or_create(
            name=PERMISSION_READ_DOCUMENT
        )
        permission_for_collab = PermissionForCollabDocument.objects.create(
            document=document_middle,
            permission=collab_permission_read,
            group_has_permission=self.base_fixtures["groups"][0],
        )
        self.assertTrue(
            CollabDocument.user_has_permission_read(document_middle.path, user)
        )
        self.assertTrue(
            CollabDocument.user_has_permission_read(
                document_middle.path + "/aksdf/asdfjajksdf/anotherone/subsub document",
                user,
            )
        )
        self.assertFalse(
            CollabDocument.user_has_permission_read(
                document_middle.path + "a/aksdf/asdfjajksdf/anotherone/subsub document",
                user,
            )
        )

        permission_for_collab.delete()
        collab_permission_write, created = CollabPermission.objects.get_or_create(
            name=PERMISSION_WRITE_DOCUMENT
        )
        permission_for_collab = PermissionForCollabDocument.objects.create(
            document=document_middle,
            permission=collab_permission_write,
            group_has_permission=self.base_fixtures["groups"][0],
        )
        self.assertTrue(
            CollabDocument.user_has_permission_read(document_middle.path, user)
        )
        self.assertTrue(
            CollabDocument.user_has_permission_read(
                document_middle.path + "/aksdf/asdfjajksdf/anotherone/subsub document",
                user,
            )
        )
        self.assertFalse(
            CollabDocument.user_has_permission_read(
                document_middle.path + "a/aksdf/asdfjajksdf/anotherone/subsub document",
                user,
            )
        )

        permission_for_collab.delete()

        permission, _ = Permission.objects.get_or_create(
            name=PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC
        )
        HasPermission.objects.create(
            group_has_permission=self.base_fixtures["groups"][0],
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
        )
        self.assertTrue(
            CollabDocument.user_has_permission_read(document_middle.path, user)
        )
        self.assertTrue(
            CollabDocument.user_has_permission_read(
                document_middle.path + "/aksdf/asdfjajksdf/anotherone/subsub document",
                user,
            )
        )
        self.assertTrue(
            CollabDocument.user_has_permission_read(
                document_middle.path + "a/aksdf/asdfjajksdf/anotherone/subsub document",
                user,
            )
        )


class CollabDocumentViewSetTest(TransactionTestCase):
    # TODO: wrong rlc, unauthenticated
    def setUp(self) -> None:
        self.urls_edit_collab = "/api/collab/edit_collab_document/"
        self.urls_collab_documents = "/api/collab/collab_documents/"

        self.base_fixtures = CreateFixtures.create_base_fixtures()
        self.base_client: APIClient = self.base_fixtures["users"][0]["client"]
        self.foreign_rlc = CreateFixtures.create_foreign_rlc_fixture()

        self.full_write_permission, created = Permission.objects.get_or_create(
            name=PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC
        )
        self.collab_write_permission, created = CollabPermission.objects.get_or_create(
            name=PERMISSION_WRITE_DOCUMENT
        )
        self.collab_read_permission, created = CollabPermission.objects.get_or_create(
            name=PERMISSION_READ_DOCUMENT
        )

    def add_document_structure(self):
        doc_top = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="top_doc",
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_top_2 = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="atop_doc",
            creator=self.base_fixtures["users"][0]["user"],
        )

        doc_middle = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="{}/{}".format(doc_top.path, "middle_doc"),
            creator=self.base_fixtures["users"][0]["user"],
        )

        doc_bottom = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="{}/{}".format(doc_middle.path, "bottom_doc"),
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_bottom_first = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="{}/{}".format(doc_middle.path, "a first bottom"),
            creator=self.base_fixtures["users"][0]["user"],
        )
        return doc_top, doc_top_2, doc_middle, doc_bottom, doc_bottom_first

    def test_list_documents_none(self):
        self.add_document_structure()

        response: Response = self.base_client.get(self.urls_collab_documents,)
        self.assertEqual(0, response.data.__len__())

    def test_list_documents_overall(self):
        (
            doc_top,
            doc_top_2,
            doc_middle,
            doc_bottom,
            doc_bottom_first,
        ) = self.add_document_structure()

        HasPermission.objects.create(
            group_has_permission=self.base_fixtures["groups"][0],
            permission=self.full_write_permission,
            permission_for_rlc=self.base_fixtures["rlc"],
        )
        response: Response = self.base_client.get(self.urls_collab_documents,)
        self.assertEqual(2, response.data.__len__())
        self.assertEqual(doc_top_2.id, response.data[0]["pk"])
        self.assertEqual(doc_top.id, response.data[1]["pk"])
        self.assertEqual(1, response.data[1]["child_pages"].__len__())
        self.assertEqual(doc_middle.id, response.data[1]["child_pages"][0]["pk"])
        self.assertEqual(
            doc_bottom.id, response.data[1]["child_pages"][0]["child_pages"][1]["pk"],
        )

    def test_list_documents_middle(self):
        (
            doc_top,
            doc_top_2,
            doc_middle,
            doc_bottom,
            doc_bottom_first,
        ) = self.add_document_structure()

        PermissionForCollabDocument.objects.create(
            document=doc_middle,
            permission=self.collab_write_permission,
            group_has_permission=self.base_fixtures["groups"][0],
        )

        response: Response = self.base_client.get(self.urls_collab_documents)
        self.assertEqual(1, response.data.__len__())
        self.assertEqual(doc_top.id, response.data[0]["pk"])
        self.assertEqual(1, response.data[0]["child_pages"].__len__())
        self.assertEqual(doc_middle.id, response.data[0]["child_pages"][0]["pk"])
        self.assertEqual(2, response.data[0]["child_pages"][0]["child_pages"].__len__())
        self.assertEqual(
            doc_bottom.id, response.data[0]["child_pages"][0]["child_pages"][1]["pk"],
        )
        self.assertEqual(
            doc_bottom_first.id,
            response.data[0]["child_pages"][0]["child_pages"][0]["pk"],
        )

    def test_list_documents_top(self):
        (
            doc_top,
            doc_top_2,
            doc_middle,
            doc_bottom,
            doc_bottom_first,
        ) = self.add_document_structure()

        PermissionForCollabDocument.objects.create(
            document=doc_top,
            permission=self.collab_write_permission,
            group_has_permission=self.base_fixtures["groups"][0],
        )

        response: Response = self.base_client.get(self.urls_collab_documents)
        self.assertEqual(1, response.data.__len__())
        self.assertEqual(doc_top.id, response.data[0]["pk"])
        self.assertEqual(1, response.data[0]["child_pages"].__len__())
        self.assertEqual(doc_middle.id, response.data[0]["child_pages"][0]["pk"])
        self.assertEqual(2, response.data[0]["child_pages"][0]["child_pages"].__len__())
        self.assertEqual(
            doc_bottom.id, response.data[0]["child_pages"][0]["child_pages"][1]["pk"],
        )
        self.assertEqual(
            doc_bottom_first.id,
            response.data[0]["child_pages"][0]["child_pages"][0]["pk"],
        )

    def test_list_documents_top_2(self):
        (
            doc_top,
            doc_top_2,
            doc_middle,
            doc_bottom,
            doc_bottom_first,
        ) = self.add_document_structure()

        PermissionForCollabDocument.objects.create(
            document=doc_top_2,
            permission=self.collab_write_permission,
            group_has_permission=self.base_fixtures["groups"][0],
        )

        response: Response = self.base_client.get(self.urls_collab_documents)
        self.assertEqual(1, response.data.__len__())
        self.assertEqual(doc_top_2.id, response.data[0]["pk"])
        self.assertEqual(0, response.data[0]["child_pages"].__len__())

    def test_list_documents_bottom(self):
        (
            doc_top,
            doc_top_2,
            doc_middle,
            doc_bottom,
            doc_bottom_first,
        ) = self.add_document_structure()

        PermissionForCollabDocument.objects.create(
            document=doc_bottom,
            permission=self.collab_write_permission,
            group_has_permission=self.base_fixtures["groups"][0],
        )

        response: Response = self.base_client.get(self.urls_collab_documents)
        self.assertEqual(1, response.data.__len__())
        self.assertEqual(doc_top.id, response.data[0]["pk"])
        self.assertEqual(1, response.data[0]["child_pages"].__len__())
        self.assertEqual(doc_middle.id, response.data[0]["child_pages"][0]["pk"])
        self.assertEqual(1, response.data[0]["child_pages"][0]["child_pages"].__len__())
        self.assertEqual(
            doc_bottom.id, response.data[0]["child_pages"][0]["child_pages"][0]["pk"],
        )

    def test_create_collab_document(self):
        self.assertEqual(0, CollabDocument.objects.count())

        response: Response = self.base_client.post(
            self.urls_collab_documents, {"path": "test document 1"}, format="json",
        )
        self.assertEqual(1, CollabDocument.objects.count())

        from_db: CollabDocument = CollabDocument.objects.first()
        self.assertTrue("id" in response.data)
        self.assertEqual(response.data["id"], from_db.id)

    def test_create_dollab_document_doubled_name(self):
        doubled_path = "test doc 1"
        CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path=doubled_path,
            creator=self.base_fixtures["users"][0]["user"],
        )

        response: Response = self.base_client.post(
            self.urls_collab_documents, {"path": doubled_path}, format="json",
        )
        self.assertEqual(2, CollabDocument.objects.count())
        self.assertTrue("id" in response.data)
        self.assertTrue("path" in response.data)
        self.assertEqual(doubled_path + "(1)", response.data["path"])
        self.assertEqual(1, CollabDocument.objects.filter(path=doubled_path).count())
        self.assertEqual(
            1, CollabDocument.objects.filter(path=doubled_path + "(1)").count(),
        )

    def test_create_collab_document_with_parent_id_no_write(self):
        first_document = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="top document",
            creator=self.base_fixtures["users"][0]["user"],
        )

        response: Response = self.base_client.post(
            self.urls_collab_documents,
            {"path": "{}/test document 1".format(first_document.path)},
            format="json",
        )
        self.assertEqual(1, CollabDocument.objects.count())
        self.assertEqual(403, response.status_code)

        has_permission = HasPermission.objects.create(
            group_has_permission=self.base_fixtures["groups"][0],
            permission=self.full_write_permission,
            permission_for_rlc=self.base_fixtures["rlc"],
        )
        response: Response = self.base_client.post(
            self.urls_collab_documents,
            {"path": "{}/test document 1".format(first_document.path)},
            format="json",
        )
        self.assertEqual(2, CollabDocument.objects.count())
        self.assertEqual(201, response.status_code)

        has_permission.delete()
        PermissionForCollabDocument.objects.create(
            group_has_permission=self.base_fixtures["groups"][0],
            permission=self.collab_write_permission,
            document=first_document,
        )

        response: Response = self.base_client.post(
            self.urls_collab_documents,
            {"path": "{}/test document 2".format(first_document.path)},
            format="json",
        )
        self.assertEqual(3, CollabDocument.objects.count())
        self.assertEqual(201, response.status_code)

        another_document = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="top document 2",
            creator=self.base_fixtures["users"][0]["user"],
        )
        response: Response = self.base_client.post(
            self.urls_collab_documents,
            {"path": "{}/test document 1".format(another_document.path)},
            format="json",
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual(4, CollabDocument.objects.count())

    def test_create_collab_document_with_wrong_parent_id(self):
        CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="parent document",
            creator=self.base_fixtures["users"][0]["user"],
        )

        response: Response = self.base_client.post(
            self.urls_collab_documents,
            {"path": "parent document 1/test document 1"},
            format="json",
        )
        self.assertEqual(1, CollabDocument.objects.count())
        self.assertEqual(400, response.status_code)  # TODO: with permissions

    def test_list_documents_foreign_rlc(self):
        document = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="test doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        document2 = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="test doc 2",
            creator=self.base_fixtures["users"][0]["user"],
        )
        HasPermission.objects.create(
            group_has_permission=self.base_fixtures["groups"][0],
            permission=self.full_write_permission,
            permission_for_rlc=self.base_fixtures["rlc"],
        )

        CollabDocument.objects.create(
            rlc=self.foreign_rlc["rlc"],
            path="test doc 2",
            creator=self.foreign_rlc["users"][0]["user"],
        )

        response: Response = self.base_client.get(self.urls_collab_documents,)
        self.assertEqual(2, response.data.__len__())
        ids = [item["pk"] for item in response.data]
        self.assertIn(document.id, ids)
        self.assertIn(document2.id, ids)

    def test_delete_document(self):
        doc_1 = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="top doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_2 = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="top doc 2",
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_1_1 = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="{}/middle doc 1".format(doc_1.path),
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_1_2 = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="{}/middle doc 2".format(doc_1.path),
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_1_1_1 = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="{}/bottom doc 1".format(doc_1_1.path),
            creator=self.base_fixtures["users"][0]["user"],
        )
        self.assertEqual(5, CollabDocument.objects.count())
        self.assertEqual(5, TextDocument.objects.count())

        client: APIClient = self.base_fixtures["users"][0]["client"]
        url = "{}{}/".format(self.urls_collab_documents, doc_1_1.id)
        response: Response = client.delete(url)

        self.assertEqual(5, CollabDocument.objects.count())
        self.assertEqual(5, TextDocument.objects.count())
        self.assertEqual(403, response.status_code)

        has_permission = HasPermission.objects.create(
            group_has_permission=self.base_fixtures["groups"][0],
            permission=self.full_write_permission,
            permission_for_rlc=self.base_fixtures["rlc"],
        )
        response: Response = client.delete(url)
        self.assertEqual(3, CollabDocument.objects.count())
        self.assertEqual(3, TextDocument.objects.count())
        self.assertEqual(204, response.status_code)

        has_permission.delete()
        PermissionForCollabDocument.objects.create(
            group_has_permission=self.base_fixtures["groups"][0],
            permission=self.collab_write_permission,
            document=doc_1,
        )
        url = "{}{}/".format(self.urls_collab_documents, doc_1_2.id)
        response: Response = client.delete(url)
        self.assertEqual(2, CollabDocument.objects.count())
        self.assertEqual(2, TextDocument.objects.count())
        self.assertEqual(204, response.status_code)

    def test_delete_document_same_start(self):
        doc_1 = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="top doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_12 = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="top doc 1 2",
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_13 = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="top doc 1 3",
            creator=self.base_fixtures["users"][0]["user"],
        )

        client: APIClient = self.base_fixtures["users"][0]["client"]
        url = "{}{}/".format(self.urls_collab_documents, doc_1.id)
        response: Response = client.delete(url)
        # TODO: with permissions

        self.assertEqual(2, CollabDocument.objects.count())
        self.assertEqual(2, TextDocument.objects.count())


class CollabDocumentPermissionsViewSetTest(TransactionTestCase):
    def setUp(self) -> None:
        self.urls_edit_collab = "/api/collab/edit_collab_document/"
        self.urls_collab_documents = "/api/collab/collab_documents/"

        self.base_fixtures = CreateFixtures.create_base_fixtures()
        self.base_client: APIClient = self.base_fixtures["users"][0]["client"]
        self.foreign_rlc = CreateFixtures.create_foreign_rlc_fixture()

        self.full_write_permission, created = Permission.objects.get_or_create(
            name=PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC
        )
        self.collab_write_permission, created = CollabPermission.objects.get_or_create(
            name=PERMISSION_WRITE_DOCUMENT
        )

    def test_get_permission_for_document(self):
        permission: CollabPermission = CollabPermission.objects.create(
            name="test_permission"
        )
        document = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="test doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        permission_for_collab_document = PermissionForCollabDocument.objects.create(
            group_has_permission=self.base_fixtures["groups"][0],
            permission=permission,
            document=document,
        )
        HasPermission.objects.create(
            permission=Permission.objects.get(
                name=PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC
            ),
            group_has_permission=self.base_fixtures["groups"][0],
            permission_for_rlc=self.base_fixtures["rlc"],
        )

        client: APIClient = self.base_fixtures["users"][0]["client"]
        url = "{}{}/permissions/".format(self.urls_collab_documents, document.id)
        response: Response = client.get(url)

        self.assertEqual(200, response.status_code)

    def test_get_permisssion_for_document_complicated(self):
        permission: CollabPermission = CollabPermission.objects.create(
            name="test_permission"
        )
        doc_1 = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="top doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_2 = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="top doc 2",
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_1_1 = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="{}/middle doc 1".format(doc_1.path),
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_1_2 = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="{}/middle doc 2".format(doc_1.path),
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_1_1_1 = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="{}/bottom doc 1".format(doc_1_1.path),
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_1_1_2 = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="{}/bottom doc 2".format(doc_1_1.path),
            creator=self.base_fixtures["users"][0]["user"],
        )

        permission_for_doc_1_1 = PermissionForCollabDocument.objects.create(
            group_has_permission=self.base_fixtures["groups"][0],
            permission=permission,
            document=doc_1_1,
        )
        permission_for_doc_1_1_1 = PermissionForCollabDocument.objects.create(
            group_has_permission=self.base_fixtures["groups"][1],
            permission=permission,
            document=doc_1_1_1,
        )
        permission_for_doc_1_1_2 = PermissionForCollabDocument.objects.create(
            group_has_permission=self.base_fixtures["groups"][1],
            permission=permission,
            document=doc_1_1_2,
        )
        permission_for_doc_1 = PermissionForCollabDocument.objects.create(
            group_has_permission=self.base_fixtures["groups"][2],
            permission=permission,
            document=doc_1,
        )
        permission_for_doc_2 = PermissionForCollabDocument.objects.create(
            group_has_permission=self.base_fixtures["groups"][2],
            permission=permission,
            document=doc_2,
        )

        # general permission
        general_manage_permission = HasPermission.objects.create(
            permission=Permission.objects.get(
                name=PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC
            ),
            group_has_permission=self.base_fixtures["groups"][0],
            permission_for_rlc=self.base_fixtures["rlc"],
        )
        unimportant_general_permission = HasPermission.objects.create(
            permission=Permission.objects.get(name=PERMISSION_MANAGE_GROUPS_RLC),
            group_has_permission=self.base_fixtures["groups"][0],
            permission_for_rlc=self.base_fixtures["rlc"],
        )

        client: APIClient = self.base_fixtures["users"][0]["client"]
        url = "{}{}/permissions/".format(self.urls_collab_documents, doc_1_1.id)
        response: Response = client.get(url)

        self.assertEqual(200, response.status_code)
        # response should contain: from_above, from_below, direct, general
        self.assertEqual(4, len(response.data))
        # from above
        self.assertIn("from_above", response.data)
        self.assertEqual(1, len(response.data["from_above"]))
        self.assertEqual(permission_for_doc_1.id, response.data["from_above"][0]["id"])
        # from below
        self.assertIn("from_below", response.data)
        self.assertEqual(2, len(response.data["from_below"]))
        self.assertEqual(
            permission_for_doc_1_1_1.id, response.data["from_below"][0]["id"]
        )
        self.assertEqual(
            permission_for_doc_1_1_2.id, response.data["from_below"][1]["id"]
        )
        # direct
        self.assertIn("direct", response.data)
        self.assertEqual(1, len(response.data["direct"]))
        self.assertEqual(permission_for_doc_1_1.id, response.data["direct"][0]["id"])
        # general
        self.assertIn("general", response.data)
        self.assertEqual(1, len(response.data["general"]))
        self.assertEqual(
            general_manage_permission.id, response.data["general"][0]["id"]
        )

        # test for doc_1_1_1
        url = "{}{}/permissions/".format(self.urls_collab_documents, doc_1_1_1.id)
        response: Response = client.get(url)

        self.assertEqual(200, response.status_code)
        # response should contain: from_above, from_below, direct, general
        self.assertEqual(4, len(response.data))
        # from above
        self.assertIn("from_above", response.data)
        self.assertEqual(2, len(response.data["from_above"]))
        self.assertEqual(permission_for_doc_1.id, response.data["from_above"][0]["id"])
        self.assertEqual(
            permission_for_doc_1_1.id, response.data["from_above"][1]["id"]
        )
        # from below
        self.assertIn("from_above", response.data)
        self.assertEqual(0, len(response.data["from_below"]))
        # direct
        self.assertIn("direct", response.data)
        self.assertEqual(1, len(response.data["direct"]))
        self.assertEqual(permission_for_doc_1_1_1.id, response.data["direct"][0]["id"])

    def test_add_document_permission(self):
        doc = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="top doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        group: Group = self.base_fixtures["groups"][0]

        self.assertEqual(0, PermissionForCollabDocument.objects.count())
        client: APIClient = self.base_fixtures["users"][0]["client"]
        url = "{}{}/permissions/".format(self.urls_collab_documents, doc.id)
        response: Response = client.post(
            url,
            {"group_id": group.id, "permission_id": self.collab_write_permission.id,},
        )

        self.assertEqual(201, response.status_code)
        self.assertEqual(1, PermissionForCollabDocument.objects.count())

    def test_add_document_permission_missing_param(self):
        doc = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="top doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        group: Group = self.base_fixtures["groups"][0]

        self.assertEqual(0, PermissionForCollabDocument.objects.count())
        client: APIClient = self.base_fixtures["users"][0]["client"]
        url = "{}{}/permissions/".format(self.urls_collab_documents, doc.id)
        response: Response = client.post(
            url, {"permission_id": self.collab_write_permission.id,},
        )

        self.assertEqual(400, response.status_code)

    def test_add_document_permission_wrong_group_id(self):
        doc = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            path="top doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        group: Group = self.base_fixtures["groups"][0]

        self.assertEqual(0, PermissionForCollabDocument.objects.count())
        client: APIClient = self.base_fixtures["users"][0]["client"]
        url = "{}{}/permissions/".format(self.urls_collab_documents, doc.id)
        response: Response = client.post(
            url,
            {
                "permission_id": self.collab_write_permission.id,
                "group_id": group.id + 100,
            },
        )

        self.assertEqual(400, response.status_code)
