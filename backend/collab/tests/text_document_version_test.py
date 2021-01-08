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
    TextDocumentVersion,
)
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.static.encryption import AESEncryption
from backend.static import error_codes
from backend.static.mocks import mock_datetime_now


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
        timezone.now = mock_datetime_now(1, 0)
        private_key = self.base_fixtures["users"][0]["private"]
        document = TextDocument(
            rlc=self.base_fixtures["rlc"],
            name="first document",
            creator=self.base_fixtures["users"][1]["user"],
            last_editor=self.base_fixtures["users"][1]["user"],
            created=timezone.now(),
            last_edited=timezone.now(),
        )
        document.save()

        timezone.now = mock_datetime_now(3, 0)
        content = "hello there how are you </adsfadf>"

        url = self.urls_text_document_versions.format(document.id)
        response: Response = self.base_client.post(
            url,
            {"content": content, "is_draft": True},
            format="json",
            **{"HTTP_PRIVATE_KEY": private_key}
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(content, response.data["content"])

        self.assertEqual(
            1, TextDocumentVersion.objects.all().count(),
        )
        self.assertEqual(1, TextDocument.objects.all().count())

        document_from_db = TextDocument.objects.first()
        self.assertEqual(1, document_from_db.versions.all().count())
        self.assertEqual(timezone.now(), document_from_db.last_edited)
        self.assertEqual(
            self.base_fixtures["users"][0]["user"], document_from_db.last_editor
        )

        version_from_db = TextDocumentVersion.objects.first()
        self.assertEqual(version_from_db.document, document_from_db)

        # TODO: second version, user not from rlc, user no permissions?

    def test_add_second_draft(self):
        # draft before should be deleted / overwritten
        private_key = self.base_fixtures["users"][0]["private"]
        document = TextDocument(
            rlc=self.base_fixtures["rlc"],
            name="first document",
            creator=self.base_fixtures["users"][1]["user"],
            last_editor=self.base_fixtures["users"][1]["user"],
            created=timezone.now(),
            last_edited=timezone.now(),
        )
        document.save()
        content = "hello there how are you </adsfadf>"

        url = self.urls_text_document_versions.format(document.id)
        response: Response = self.base_client.post(
            url,
            {"content": content, "is_draft": True},
            format="json",
            **{"HTTP_PRIVATE_KEY": private_key}
        )
        self.assertEqual(201, response.status_code)

        content = "another version, some changes, all overwritten"
        response: Response = self.base_client.post(
            url,
            {"content": content, "is_draft": True},
            format="json",
            **{"HTTP_PRIVATE_KEY": private_key}
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(1, TextDocumentVersion.objects.count())

    def test_create_public_after_draft(self):
        private_key = self.base_fixtures["users"][0]["private"]
        document = TextDocument(
            rlc=self.base_fixtures["rlc"],
            name="first document",
            creator=self.base_fixtures["users"][1]["user"],
            last_editor=self.base_fixtures["users"][1]["user"],
            created=timezone.now(),
            last_edited=timezone.now(),
        )
        document.save()
        content = "hello there how are you </adsfadf>"

        url = self.urls_text_document_versions.format(document.id)
        response: Response = self.base_client.post(
            url,
            {"content": content, "is_draft": True},
            format="json",
            **{"HTTP_PRIVATE_KEY": private_key}
        )
        self.assertEqual(201, response.status_code)

        content = "another version, some changes, all overwritten"
        response: Response = self.base_client.post(
            url,
            {"content": content, "is_draft": False},
            format="json",
            **{"HTTP_PRIVATE_KEY": private_key}
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(1, TextDocumentVersion.objects.count())

    def test_create_second_public_version(self):
        private_key = self.base_fixtures["users"][0]["private"]
        document = TextDocument(
            rlc=self.base_fixtures["rlc"],
            name="first document",
            creator=self.base_fixtures["users"][1]["user"],
            last_editor=self.base_fixtures["users"][1]["user"],
            created=timezone.now(),
            last_edited=timezone.now(),
        )
        document.save()
        content = "hello there how are you </adsfadf>"

        url = self.urls_text_document_versions.format(document.id)
        response: Response = self.base_client.post(
            url,
            {"content": content, "is_draft": False},
            format="json",
            **{"HTTP_PRIVATE_KEY": private_key}
        )
        self.assertEqual(201, response.status_code)

        content = "another version, some changes, all overwritten"
        response: Response = self.base_client.post(
            url,
            {"content": content, "is_draft": False},
            format="json",
            **{"HTTP_PRIVATE_KEY": private_key}
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(2, TextDocumentVersion.objects.count())
        document_from_db = TextDocument.objects.first()
        self.assertEqual(2, document_from_db.versions.count())

    def test_create_not_existing_document(self):
        private_key = self.base_fixtures["users"][0]["private"]
        document = TextDocument(
            rlc=self.base_fixtures["rlc"],
            name="first document",
            creator=self.base_fixtures["users"][0]["user"],
        )
        document.save()

        url = self.urls_text_document_versions.format(document.id + 1)
        response: Response = self.base_client.post(
            url,
            {"content": "testt", "is_draft": True},
            format="json",
            **{"HTTP_PRIVATE_KEY": private_key}
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__ID_NOT_FOUND["error_code"],
            response.data["error_code"],
        )

    def test_create_params_missing(self):
        private_key = self.base_fixtures["users"][0]["private"]
        document = TextDocument(
            rlc=self.base_fixtures["rlc"],
            name="first document",
            creator=self.base_fixtures["users"][0]["user"],
        )
        document.save()
        url = self.urls_text_document_versions.format(document.id)

        response: Response = self.base_client.post(
            url, {"content": "sad"}, format="json", **{"HTTP_PRIVATE_KEY": private_key}
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__PARAMS_NOT_VALID["error_code"],
            response.data["error_code"],
        )

        response: Response = self.base_client.post(
            url, {"is_draft": True}, format="json", **{"HTTP_PRIVATE_KEY": private_key}
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__PARAMS_NOT_VALID["error_code"],
            response.data["error_code"],
        )

        response: Response = self.base_client.post(
            url, {}, format="json", **{"HTTP_PRIVATE_KEY": private_key}
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__PARAMS_NOT_VALID["error_code"],
            response.data["error_code"],
        )

    def test_get_versions(self):
        private_key = self.base_fixtures["users"][0]["private"]
        document = TextDocument(
            rlc=self.base_fixtures["rlc"],
            name="first document",
            creator=self.base_fixtures["users"][0]["user"],
        )
        document.save()

        user0: UserProfile = self.base_fixtures["users"][0]["user"]
        rlcs_aes_key = user0.get_rlcs_aes_key(private_key)
        timezone.now = mock_datetime_now(0, 0)

        version1: TextDocumentVersion = TextDocumentVersion.create(
            "first content really interesting", False, rlcs_aes_key, user0, document
        )
        version1.created = timezone.now()
        version1.save()

        timezone.now = mock_datetime_now(3, 0)
        version2_content = "version 3 of document, changed something"
        version2: TextDocumentVersion = TextDocumentVersion.create(
            version2_content, False, rlcs_aes_key, user0, document,
        )
        version2.created = timezone.now()
        version2.save()

        timezone.now = mock_datetime_now(1, 30)
        version3: TextDocumentVersion = TextDocumentVersion.create(
            "version 2 of document, changed everything",
            False,
            rlcs_aes_key,
            user0,
            document,
        )
        version3.created = timezone.now()
        version3.save()

        url = self.urls_text_document_versions.format(document.id)
        start = datetime.now()
        response: Response = self.base_client.get(
            url, format="json", **{"HTTP_PRIVATE_KEY": private_key}
        )
        print("request duration: ", (datetime.now() - start).microseconds / 1000, "ms")
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.data)
        self.assertEqual(3, response.data.__len__())
        self.assertEqual(version2.id, response.data[0]["id"])
        self.assertEqual(version2_content, response.data[0]["content"])
        self.assertEqual(version3.id, response.data[1]["id"])
        self.assertNotIn("content", response.data[1])
        self.assertEqual(version1.id, response.data[2]["id"])
        self.assertNotIn("content", response.data[2])

    def test_get_versions_max(self):
        pass
