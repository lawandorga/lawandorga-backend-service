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

from backend.api import models as api_models
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.api.tests.statics import StaticTestMethods
from backend.recordmanagement import models as record_models
from backend.static.encryption import AESEncryption, RSAEncryption
from backend.static.permissions import (
    PERMISSION_CAN_ADD_RECORD_RLC,
    PERMISSION_CAN_CONSULT,
)


# TODO: add the encrypted client tests from example data tests to this tests
class EncryptedClientTests(TransactionTestCase):
    def setUp(self):
        self.base_fixtures = CreateFixtures.create_base_fixtures()
        users: [api_models.UserProfile] = [
            self.base_fixtures["users"][0]["user"],
            self.base_fixtures["users"][1]["user"],
            self.base_fixtures["users"][2]["user"],
        ]
        self.record_fixtures = CreateFixtures.create_record_base_fixtures(
            rlc=self.base_fixtures["rlc"], users=users
        )

    def test_client_model_patch(self):
        client: record_models.EncryptedClient = self.record_fixtures["client"]["client"]
        clients_aes_key: str = self.record_fixtures["client"]["key"]

        patch_object = {"name": "peter parker", "phone_number": "12312312"}

        client.patch(patch_object, clients_aes_key)

        client_from_db: record_models.EncryptedClient = record_models.EncryptedClient.objects.get(
            pk=client.id
        )

        self.assertEqual(
            patch_object["name"],
            AESEncryption.decrypt(client_from_db.name, clients_aes_key),
        )
        self.assertEqual(
            patch_object["phone_number"],
            AESEncryption.decrypt(client_from_db.phone_number, clients_aes_key),
        )
