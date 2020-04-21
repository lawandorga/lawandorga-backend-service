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

from backend.api import models as ApiModels
from backend.recordmanagement import models as RecordModels

from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.api.tests.statics import StaticTestMethods
from backend.static.encryption import AESEncryption, RSAEncryption
from backend.recordmanagement.models import EncryptedRecord, EncryptedRecordPermission
from backend.static.permissions import PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC


class MissingRecordKeysTests(TransactionTestCase):
    def setUp(self):
        self.add_fixtures()
        pass

    def test_command(self):
        # test if command adds all missing key entries as supposed
        pass

    def test_login(self):
        # test if missing key entries get read, keys generated and missing keys deleted
        pass

    def add_fixtures(self):
        self.base_fixtures = CreateFixtures.create_base_fixtures()
        # create records
        self.record1 = RecordModels.EncryptedRecord(record_token='record1', from_rlc=self.base_fixtures['rlc'], )

