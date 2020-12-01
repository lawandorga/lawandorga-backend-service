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

from backend.collab.models import CollabDocument, EditingRoom, TextDocument
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.static.encryption import AESEncryption
from backend.static import error_codes


class CollabDocumentConnectionTest(TransactionTestCase):
    # TODO: double connection -> one room, no valid private key?, no valid collab doc id, wrong rlc,
    def setUp(self) -> None:
        self.urls_edit_collab = "/api/collab/edit_collab_document/"
        self.urls_list_collab = "/api/collab/collab_documents/"

        self.base_fixtures = CreateFixtures.create_base_fixtures()
        self.base_client: APIClient = self.base_fixtures["users"][0]["client"]

    def test_connect_one_user(self):
        document = CollabDocument(
            rlc=self.base_fixtures["rlc"],
            parent=None,
            name="test doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        document.save()
        self.assertEqual(0, EditingRoom.objects.count())

        response: Response = self.base_client.get(
            self.urls_edit_collab + str(document.id) + "/",
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, EditingRoom.objects.count())

        room: EditingRoom = EditingRoom.objects.first()
        self.assertEqual(room.document.get_collab_document(), document)

        self.assertEqual(response.data["room_id"], room.room_id)
        self.assertEqual(response.data["password"], room.password)

    def test_unauthenticated(self):
        document = CollabDocument(
            rlc=self.base_fixtures["rlc"],
            parent=None,
            name="test doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        document.save()

        response: Response = APIClient().get(
            self.urls_edit_collab + str(document.id) + "/",
        )

        self.assertEqual(401, response.status_code)


class CollabDocumentTest(TransactionTestCase):
    # TODO: wrong rlc, unauthenticated
    def setUp(self) -> None:
        self.urls_edit_collab = "/api/collab/edit_collab_document/"
        self.urls_collab_documents = "/api/collab/collab_documents/"

        self.base_fixtures = CreateFixtures.create_base_fixtures()
        self.base_client: APIClient = self.base_fixtures["users"][0]["client"]
        self.foreign_rlc = CreateFixtures.create_foreign_rlc_fixture()

    def test_private_key_for_later(self):
        # private_key = self.base_fixtures["users"][0]["private"]
        # response: Response = self.base_client.post(
        #     self.urls_collab_documents,
        #     {},
        #     format="json",
        #     **{"HTTP_PRIVATE_KEY": private_key}
        # )
        self.assertTrue(True)

    def test_list_documents_simple(self):
        doc_top = CollabDocument(
            rlc=self.base_fixtures["rlc"],
            parent=None,
            name="top_doc",
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_top.save()
        doc_top_2 = CollabDocument(
            rlc=self.base_fixtures["rlc"],
            parent=None,
            name="atop_doc",
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_top_2.save()
        doc_middle = CollabDocument(
            rlc=self.base_fixtures["rlc"],
            parent=doc_top,
            name="middle_doc",
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_middle.save()
        doc_bottom = CollabDocument(
            rlc=self.base_fixtures["rlc"],
            parent=doc_middle,
            name="bottom_doc",
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_bottom.save()
        doc_bottom_first = CollabDocument(
            rlc=self.base_fixtures["rlc"],
            parent=doc_middle,
            name="a first",
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_bottom_first.save()

        response: Response = self.base_client.get(self.urls_collab_documents,)
        self.assertEqual(2, response.data.__len__())
        self.assertEqual(doc_top_2.id, response.data[0]["pk"])
        self.assertEqual(doc_top.id, response.data[1]["pk"])
        self.assertEqual(doc_middle.id, response.data[1]["children"][0]["pk"])
        self.assertEqual(
            doc_bottom_first.id, response.data[1]["children"][0]["children"][0]["pk"]
        )

    def test_create_collab_document(self):
        self.assertEqual(0, CollabDocument.objects.count())

        response: Response = self.base_client.post(
            self.urls_collab_documents,
            {"name": "test document 1", "parent_id": None},
            format="json",
        )
        self.assertEqual(1, CollabDocument.objects.count())

        from_db: CollabDocument = CollabDocument.objects.first()
        self.assertTrue("id" in response.data)
        self.assertEqual(response.data["id"], from_db.id)

    def test_create_dollab_document_doubled_name(self):
        doubled_name = "test doc 1"
        first_document = CollabDocument(
            rlc=self.base_fixtures["rlc"],
            parent=None,
            name=doubled_name,
            creator=self.base_fixtures["users"][0]["user"],
        )
        first_document.save()

        response: Response = self.base_client.post(
            self.urls_collab_documents,
            {"name": doubled_name, "parent_id": None},
            format="json",
        )
        self.assertEqual(2, CollabDocument.objects.count())
        self.assertTrue("id" in response.data)
        self.assertTrue("name" in response.data)
        self.assertEqual(doubled_name + " (1)", response.data["name"])
        self.assertEqual(
            1, CollabDocument.objects.filter(name=doubled_name, parent=None).count()
        )
        self.assertEqual(
            1,
            CollabDocument.objects.filter(
                name=doubled_name + " (1)", parent=None
            ).count(),
        )

    def test_create_collab_document_with_parent_id(self):
        first_document = CollabDocument(
            rlc=self.base_fixtures["rlc"],
            parent=None,
            name="parent document",
            creator=self.base_fixtures["users"][0]["user"],
        )
        first_document.save()

        response: Response = self.base_client.post(
            self.urls_collab_documents,
            {"name": "test document 1", "parent_id": first_document.id},
            format="json",
        )
        self.assertEqual(2, CollabDocument.objects.count())

        self.assertTrue("id" in response.data)
        from_db: CollabDocument = CollabDocument.objects.filter(
            pk=response.data["id"]
        ).first()
        self.assertEqual(from_db.parent, first_document)

    def test_create_collab_document_with_wrong_parent_id(self):
        first_document = CollabDocument(
            rlc=self.base_fixtures["rlc"],
            parent=None,
            name="parent document",
            creator=self.base_fixtures["users"][0]["user"],
        )
        first_document.save()

        response: Response = self.base_client.post(
            self.urls_collab_documents,
            {"name": "test document 1", "parent_id": first_document.id + 1},
            format="json",
        )
        self.assertEqual(1, CollabDocument.objects.count())
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__ID_NOT_FOUND["error_code"],
            response.data["error_code"],
        )

    def test_create_collab_document_without_parent_id(self):
        self.assertEqual(0, CollabDocument.objects.count())

        response: Response = self.base_client.post(
            self.urls_collab_documents, {"name": "test document 1"}, format="json",
        )
        self.assertEqual(1, CollabDocument.objects.count())

        from_db: CollabDocument = CollabDocument.objects.first()
        self.assertTrue("id" in response.data)
        self.assertEqual(response.data["id"], from_db.id)
        self.assertEqual(response.data["parent"], None)

    def test_list_documents_foreign_rlc(self):
        document = CollabDocument(
            rlc=self.base_fixtures["rlc"],
            parent=None,
            name="test doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        document.save()
        document2 = CollabDocument(
            rlc=self.base_fixtures["rlc"],
            parent=None,
            name="test doc 2",
            creator=self.base_fixtures["users"][0]["user"],
        )
        document2.save()

        document_foreign = CollabDocument(
            rlc=self.foreign_rlc["rlc"],
            parent=None,
            name="test doc 2",
            creator=self.foreign_rlc["users"][0]["user"],
        )
        document_foreign.save()

        response: Response = self.base_client.get(self.urls_collab_documents,)
        self.assertEqual(2, response.data.__len__())
        ids = [item["pk"] for item in response.data]
        self.assertIn(document.id, ids)
        self.assertIn(document2.id, ids)

    def test_model_get_document_from_path(self):
        doc_top = CollabDocument(
            rlc=self.base_fixtures["rlc"],
            parent=None,
            name="top_doc",
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_top.save()
        doc_middle = CollabDocument(
            rlc=self.base_fixtures["rlc"],
            parent=doc_top,
            name="middle_doc",
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_middle.save()

        doc_bottom = CollabDocument(
            rlc=self.base_fixtures["rlc"],
            parent=doc_middle,
            name="bottom_doc",
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_bottom.save()

        doc_bottom_with_dash = CollabDocument(
            rlc=self.base_fixtures["rlc"],
            parent=doc_middle,
            name="with/dash",
            creator=self.base_fixtures["users"][0]["user"],
        )
        doc_bottom_with_dash.save()

        self.assertEqual(
            doc_middle,
            CollabDocument.get_collab_document_from_path(
                "top_doc//middle_doc//", self.base_fixtures["rlc"]
            ),
        )
        self.assertEqual(
            doc_middle,
            CollabDocument.get_collab_document_from_path(
                "top_doc//middle_doc", self.base_fixtures["rlc"]
            ),
        )
        self.assertEqual(
            doc_bottom,
            CollabDocument.get_collab_document_from_path(
                "top_doc//middle_doc//bottom_doc", self.base_fixtures["rlc"]
            ),
        )
        self.assertEqual(
            doc_bottom,
            CollabDocument.get_collab_document_from_path(
                "top_doc//middle_doc//bottom_doc", self.base_fixtures["rlc"]
            ),
        )
        self.assertEqual(
            doc_bottom_with_dash,
            CollabDocument.get_collab_document_from_path(
                "top_doc//middle_doc//with/dash", self.base_fixtures["rlc"]
            ),
        )
