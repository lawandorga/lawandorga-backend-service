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

import time
from django.test import TransactionTestCase
from rest_framework.test import APIClient
from rest_framework.response import Response

from backend.recordmanagement import models as record_models
from backend.api import models as api_models
from backend.files import models as file_models
from backend.api.errors import CustomError
from backend.api.management.commands.commands import create_missing_key_entries
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.recordmanagement import models as record_models
from backend.static.encryption import AESEncryption, RSAEncryption
from backend.static.permissions import PERMISSION_MANAGE_PERMISSIONS_RLC


class RecordStatisticsTests(TransactionTestCase):
    def setUp(self) -> None:
        self.base_fixtures = CreateFixtures.create_base_fixtures()

        users: [api_models.UserProfile] = [
            self.base_fixtures["users"][0]["user"],
            self.base_fixtures["users"][1]["user"],
            self.base_fixtures["users"][2]["user"],
        ]
        self.record_fixtures = CreateFixtures.create_record_base_fixtures(
            rlc=self.base_fixtures["rlc"], users=users
        )

        self.base_client = self.base_fixtures["users"][0]["client"]
        self.base_url = "/api/records/statistics/"

    def test_first(self):
        number_of_record_tags = record_models.RecordTag.objects.count()

        response: Response = self.base_client.get(self.base_url)
        c = list(record_models.EncryptedRecord.objects.all())
        a = 10
