#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2021  Dominik Walser
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

from django.db.utils import IntegrityError
from django.utils import timezone
from django.test import TransactionTestCase
from rest_framework.response import Response
from rest_framework.test import APIClient


from backend.api.models import UserProfile, Rlc
from backend.recordmanagement.models import EncryptedRecord
from backend.collab.models import (
    CollabDocument,
    PermissionForCollabDocument,
    CollabPermission,
)
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.static.encryption import AESEncryption
from backend.static import error_codes
from backend.static.mocks import mock_datetime_now


class TextDocumentModelTest(TransactionTestCase):
    def setUp(self) -> None:
        self.base_fixtures = CreateFixtures.create_base_fixtures()

    def test_save_doubled_permission(self):
        document = CollabDocument.objects.create(
            rlc=self.base_fixtures["rlc"],
            parent=None,
            name="test doc 1",
            creator=self.base_fixtures["users"][0]["user"],
        )
        permission = CollabPermission.objects.create(name="test_permission")

        permission_data = {
            "document": document,
            "group_has_permission": self.base_fixtures["groups"][0],
            "permission": permission,
        }

        PermissionForCollabDocument.objects.create(**permission_data)
        self.assertEqual(1, PermissionForCollabDocument.objects.count())
        try:
            PermissionForCollabDocument.objects.create(**permission_data)
        except IntegrityError as e:
            pass
        self.assertEqual(1, PermissionForCollabDocument.objects.count())
