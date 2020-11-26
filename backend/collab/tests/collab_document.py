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


class CollabDocumentConnectionTest(TransactionTestCase):
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

    # TODO: double connection -> one room, no valid private key?, no valid collab doc id, wrong rlc,


class CollabDocumentTest(TransactionTestCase):
    def setUp(self) -> None:
        self.urls_edit_collab = "/api/collab/edit_collab_document/"
        self.urls_list_collab = "/api/collab/collab_documents/"

        self.base_fixtures = CreateFixtures.create_base_fixtures()
        self.base_client: APIClient = self.base_fixtures["users"][0]["client"]

    def test_list_documents(self):
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

        response: Response = self.base_client.get(self.urls_list_collab,)
        self.assertEqual(2, response.data.__len__())
        ids = [item["pk"] for item in response.data]
        self.assertIn(document.id, ids)
        # TODO: wrong rlc, unauthenticated,
