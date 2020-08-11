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

import time
from django.test import TransactionTestCase
from rest_framework.test import APIClient

from backend.api import models as api_models
from backend.files import models as file_models
from backend.api.errors import CustomError
from backend.api.management.commands.commands import create_missing_key_entries
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.recordmanagement import models as record_models
from backend.static.encryption import AESEncryption, RSAEncryption
from backend.static.permissions import PERMISSION_MANAGE_PERMISSIONS_RLC


# TODO: check if permission is given to anyone, if encryption key is added
class MissingRecordKeysTests(TransactionTestCase):
    def setUp(self):
        self.base_fixtures = CreateFixtures.create_base_fixtures()
        self.superuser = CreateFixtures.create_superuser()
        self.local_fixtures = self.add_fixtures()

    def tearDown(self):
        api_models.Permission.objects.all().delete()
        api_models.UserProfile.objects.all().delete()
        api_models.UserEncryptionKeys.objects.all().delete()
        api_models.RlcEncryptionKeys.objects.all().delete()
        api_models.Group.objects.all().delete()
        api_models.HasPermission.objects.all().delete()
        record_models.EncryptedRecord.objects.all().delete()
        record_models.EncryptedRecordPermission.objects.all().delete()
        record_models.RecordEncryption.objects.all().delete()
        record_models.MissingRecordKey.objects.all().delete()
        file_models.FolderPermission.objects.all().delete()
        file_models.PermissionForFolder.objects.all().delete()

    def test_missing_keys_flow(self):
        # test if command adds all missing key entries as supposed

        self.assertEqual(
            self.local_fixtures["records"][0]["record"].record_token, "record1"
        )
        self.assertEqual(
            self.local_fixtures["records"][0]["record"].client,
            self.local_fixtures["client"]["client"],
        )
        record_key = self.local_fixtures["records"][0]["record"].get_decryption_key(
            self.base_fixtures["users"][0]["user"],
            self.base_fixtures["users"][0]["private"],
        )
        self.assertEqual(record_key, self.local_fixtures["records"][0]["key"])

        with self.assertRaises(CustomError):
            self.local_fixtures["records"][0]["record"].get_decryption_key(
                self.base_fixtures["users"][1]["user"],
                self.base_fixtures["users"][1]["private"],
            )
        self.assertEqual(record_models.MissingRecordKey.objects.count(), 0)
        create_missing_key_entries()
        self.assertEqual(record_models.MissingRecordKey.objects.count(), 4)
        client = APIClient()

        # start = time.time()
        client.post(
            "/api/login/",
            {
                "username": self.base_fixtures["users"][0]["user"].email,
                "password": "qwe123",
            },
        )
        # print('login took: ', time.time() - start)

        self.assertEqual(record_models.MissingRecordKey.objects.count(), 0)
        create_missing_key_entries()
        self.assertEqual(record_models.MissingRecordKey.objects.count(), 0)

    def test_measure_login_timers(self):
        repetitions = 5
        client = APIClient()
        start = time.time()
        for i in range(repetitions):
            client.post(
                "/api/login/",
                {
                    "username": self.base_fixtures["users"][0]["user"].email,
                    "password": "qwe123",
                },
            )
        end = time.time()
        print("average time:", (end - start) / repetitions)

    def test_measure_login_with_missing_keys_timers(self):
        repetitions = 5
        missing_entry_users = 5
        client = APIClient()
        time_sum = 0
        for i in range(repetitions):
            self.tearDown()
            # self.doCleanups()
            self.setUp()
            for j in range(missing_entry_users):
                MissingRecordKeysTests.create_user_with_missing_key_entry(
                    "timeuser" + str(j),
                    self.base_fixtures["rlc"],
                    [
                        self.local_fixtures["records"][0]["record"],
                        self.local_fixtures["records"][1]["record"],
                    ],
                )
            self.assertEqual(
                record_models.MissingRecordKey.objects.count(), missing_entry_users * 2
            )
            starttime = time.time()
            client.post(
                "/api/login/",
                {
                    "username": self.base_fixtures["users"][0]["user"].email,
                    "password": "qwe123",
                },
            )
            time_sum += time.time() - starttime
            self.assertEqual(record_models.MissingRecordKey.objects.count(), 0)
        print("average time:", time_sum / repetitions)

    def test_login(self):
        # test if missing key entries get read, keys generated and missing keys deleted
        pass

    def add_fixtures(self):
        perm = api_models.Permission.objects.get(name=PERMISSION_MANAGE_PERMISSIONS_RLC)
        user_has_permission = api_models.HasPermission(
            user_has_permission=self.base_fixtures["users"][0]["user"],
            permission_for_rlc=self.base_fixtures["rlc"],
            permission=perm,
        )
        user_has_permission.save()
        user_has_permission = api_models.HasPermission(
            user_has_permission=self.base_fixtures["users"][2]["user"],
            permission_for_rlc=self.base_fixtures["rlc"],
            permission=perm,
        )
        user_has_permission.save()

        return_object = {}

        # create client
        aes_client_key = AESEncryption.generate_secure_key()
        e_client = record_models.EncryptedClient(from_rlc=self.base_fixtures["rlc"])
        e_client.name = AESEncryption.encrypt("MainClient", aes_client_key)
        e_client.note = AESEncryption.encrypt(
            "important MainClient note", aes_client_key
        )
        e_client.save()
        e_client = e_client
        client_obj = {"client": e_client, "key": aes_client_key}
        return_object.update({"client": client_obj})

        # create records
        records = []
        # 1
        record1 = MissingRecordKeysTests.add_record(
            token="record1",
            rlc=self.base_fixtures["rlc"],
            client=e_client,
            creator=self.base_fixtures["users"][0]["user"],
            note="record1 note",
            working_on_record=[self.base_fixtures["users"][1]["user"]],
            with_record_permission=[],
            with_encryption_keys=[
                self.base_fixtures["users"][0]["user"],
                self.base_fixtures["users"][2]["user"],
                self.superuser["user"],
            ],
        )
        records.append(record1)
        # 2
        record2 = MissingRecordKeysTests.add_record(
            token="record2",
            rlc=self.base_fixtures["rlc"],
            client=e_client,
            creator=self.base_fixtures["users"][0]["user"],
            note="record2 note",
            working_on_record=[self.base_fixtures["users"][0]["user"]],
            with_record_permission=[self.base_fixtures["users"][1]["user"]],
            with_encryption_keys=[self.base_fixtures["users"][0]["user"]],
        )
        records.append(record2)

        return_object.update({"records": records})

        return return_object

    @staticmethod
    def add_record(
        token,
        rlc,
        client,
        creator,
        note,
        working_on_record,
        with_record_permission,
        with_encryption_keys,
    ):
        aes_key = AESEncryption.generate_secure_key()
        record = record_models.EncryptedRecord(
            record_token=token, from_rlc=rlc, creator=creator, client=client
        )
        record.note = AESEncryption.encrypt(note, aes_key)
        record.save()

        for user in working_on_record:
            record.working_on_record.add(user)
        record.save()

        for user in with_record_permission:
            permission = record_models.EncryptedRecordPermission(
                request_from=user,
                request_processed=creator,
                record=record,
                can_edit=True,
                state="gr",
            )
            permission.save()

        for user in with_encryption_keys:
            MissingRecordKeysTests.add_encryption_key(user, record, aes_key)

        return {"record": record, "key": aes_key}

    @staticmethod
    def add_encryption_key(user, record, key):
        pub = user.get_public_key()
        encrypted_key = RSAEncryption.encrypt(key, pub)
        record_encryption = record_models.RecordEncryption(
            user=user, record=record, encrypted_key=encrypted_key
        )
        record_encryption.save()

    @staticmethod
    def create_user_with_missing_key_entry(name, rlc, records):
        pot_users = api_models.UserProfile.objects.filter(name=name)
        if pot_users.count() < 1:
            user = CreateFixtures.create_user(rlc, name)["user"]
        else:
            user = pot_users.first()
        for record in records:
            missing = record_models.MissingRecordKey(record=record, user=user)
            missing.save()
