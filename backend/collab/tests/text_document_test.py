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

from backend.api.models import UserProfile, Rlc
from backend.recordmanagement.models import EncryptedRecord
from backend.collab.models import (
    CollabDocument,
    EditingRoom,
    TextDocument,
    RecordDocument,
)
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.static.encryption import AESEncryption
from backend.static import error_codes


class TextDocumentTest(TransactionTestCase):
    def setUp(self) -> None:
        self.urls_text_documents = "/api/collab/text_documents/"

        self.base_fixtures = CreateFixtures.create_base_fixtures()
        self.base_client: APIClient = self.base_fixtures["users"][0]["client"]
        self.foreign_rlc = CreateFixtures.create_foreign_rlc_fixture()
        # TODO: foreign RLC, unauthenticated, no private
        # TODO: list, post methods? close them!

    def test_get_collab_document(self):
        private_key = self.base_fixtures["users"][0]["private"]
        user: UserProfile = self.base_fixtures["users"][0]["user"]
        rlcs_aes: str = user.get_rlcs_aes_key(private_key)
        content = "hello there, in this document is important information"
        encrypted_content = AESEncryption.encrypt(content, rlcs_aes)

        first_document = CollabDocument(
            rlc=self.base_fixtures["rlc"],
            parent=None,
            name="first document",
            creator=self.base_fixtures["users"][0]["user"],
            content=encrypted_content,
        )
        first_document.save()

        response: Response = self.base_client.get(
            self.urls_text_documents + str(first_document.id) + "/",
            format="json",
            **{"HTTP_PRIVATE_KEY": private_key}
        )
        self.assertEqual(200, response.status_code)
        self.assertTrue("id" in response.data)
        self.assertEqual(first_document.id, response.data["id"])
        self.assertTrue("name" in response.data)
        self.assertEqual(first_document.name, response.data["name"])
        self.assertTrue("content" in response.data)
        self.assertEqual(content, response.data["content"])

    def test_indexes(self):
        users: [UserProfile] = [
            self.base_fixtures["users"][0]["user"],
            self.base_fixtures["users"][1]["user"],
            self.base_fixtures["users"][2]["user"],
        ]
        rlc: Rlc = self.base_fixtures["rlc"]
        record_fixtures = CreateFixtures.create_record_base_fixtures(
            rlc=rlc, users=users
        )
        record: EncryptedRecord = record_fixtures["records"][0]["record"]
        user: UserProfile = self.base_fixtures["users"][0]["user"]

        record_doc_1 = RecordDocument(
            record=record, name="rec doc 1", rlc=rlc, creator=user
        )
        record_doc_1.save()
        collab_doc_1 = CollabDocument(
            parent=None, name="collab doc 1", rlc=rlc, creator=user
        )
        collab_doc_1.save()

        text_doc_2: TextDocument = TextDocument.objects.get(pk=collab_doc_1.id)
        self.assertEqual(text_doc_2.get_collab_document(), collab_doc_1)
