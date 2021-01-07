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

from datetime import date, datetime
from django.utils import timezone
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


class TextDocumentVersionViewSetTest(TransactionTestCase):
    def setUp(self) -> None:
        self.base_fixtures = CreateFixtures.create_base_fixtures()

    def test_create(self):
        pass


class VersionsOfTextDocumentsViewSetTest(TransactionTestCase):
    def setUp(self) -> None:
        self.urls_text_document_versions = "/api/collab/text_documents/{}/versions/"
        self.base_fixtures = CreateFixtures.create_base_fixtures()
        self.base_client: APIClient = self.base_fixtures["users"][0]["client"]

    def test_create_new_version(self):
        private_key = self.base_fixtures["users"][0]["private"]
        document = TextDocument(
            rlc=self.base_fixtures["rlc"],
            name="first document",
            creator=self.base_fixtures["users"][0]["user"],
            content=b"",
        )
        document.save()

        url = self.urls_text_document_versions.format(document.id)

        response: Response = self.base_client.post(
            url, format="json", **{"HTTP_PRIVATE_KEY": private_key}
        )
        self.assertEqual(201, response.status_code)
