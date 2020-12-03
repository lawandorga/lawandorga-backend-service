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


class EditingRoomViewSetTest(TransactionTestCase):

    # TODO: wrong id, no id?, wrong rlc? , unauthenticated
    def setUp(self) -> None:
        self.urls_editing = "/api/collab/editing/"
        self.base_fixtures = CreateFixtures.create_base_fixtures()

        self.base_client: APIClient = self.base_fixtures["users"][0]["client"]
        self.private_key = self.base_fixtures["users"][0]["private"]

        self.document = TextDocument(
            rlc=self.base_fixtures["rlc"],
            name="some document",
            creator=self.base_fixtures["users"][0]["user"],
            content=bytes(),
        )
        self.document.save()

    def test_single_connection(self):
        self.assertEqual(0, EditingRoom.objects.count())

        response: Response = self.base_client.get(
            self.urls_editing + str(self.document.id) + "/"
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, EditingRoom.objects.count())
        from_db: EditingRoom = EditingRoom.objects.first()
        self.assertEqual(self.document, from_db.document)
        self.assertIn("password", response.data)
        self.assertIn("room_id", response.data)
        self.assertIn("did_create", response.data)
        self.assertEqual(from_db.password, response.data["password"])
        self.assertEqual(from_db.room_id, response.data["room_id"])
        self.assertEqual(True, response.data["did_create"])

    def test_multiple_connection(self):
        self.assertEqual(0, EditingRoom.objects.count())

        response: Response = self.base_client.get(
            self.urls_editing + str(self.document.id) + "/"
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, EditingRoom.objects.count())
        from_db: EditingRoom = EditingRoom.objects.first()

        response: Response = self.base_fixtures["users"][1]["client"].get(
            self.urls_editing + str(self.document.id) + "/"
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, EditingRoom.objects.count())
        self.assertEqual(from_db.password, response.data["password"])
        self.assertEqual(from_db.room_id, response.data["room_id"])
        self.assertEqual(False, response.data["did_create"])
