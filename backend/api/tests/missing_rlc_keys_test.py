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
from rest_framework.test import APIClient

from backend.api import models as api_models
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.recordmanagement import models as record_models
from backend.static.encryption import AESEncryption
from backend.static.permissions import PERMISSION_MANAGE_PERMISSIONS_RLC
from backend.api.management.commands.commands import create_missing_key_entries


class MissingRlcKeysTests(TransactionTestCase):
    def setUp(self):
        self.base_fixtures = CreateFixtures.create_base_fixtures()
        self.superuser = CreateFixtures.create_superuser()
        self.local_fixtures = self.add_fixtures()

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
        record1 = CreateFixtures.add_record(
            record_token="record1",
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
        record2 = CreateFixtures.add_record(
            record_token="record2",
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

    def test_full_flow(self):
        create_missing_key_entries()
        client = APIClient()
        client.post(
            "/api/login/",
            {
                "username": self.base_fixtures["users"][0]["user"].email,
                "password": "qwe123",
            },
        )

        users_email = self.base_fixtures["users"][2]["user"].email
        old_public_key = api_models.UserProfile.objects.get(
            email=users_email
        ).get_public_key()

        client.post("/api/forgot_password/", {"email": users_email})

        self.assertEqual(1, api_models.ForgotPasswordLinks.objects.all().count())

        response_from_login = client.post(
            "/api/login/", {"username": users_email, "password": "qwe123"}
        )
        self.assertEqual(200, response_from_login.status_code)
        self.assertEqual(
            2,
            record_models.RecordEncryption.objects.filter(
                user=api_models.UserProfile.objects.get(email=users_email)
            ).count(),
        )

        link = api_models.ForgotPasswordLinks.objects.first()
        response_from_reset = client.post(
            "/api/reset_password/" + link.link + "/", {"new_password": "qwe1234"}
        )
        self.assertEqual(200, response_from_reset.status_code)

        user = api_models.UserProfile.objects.get(email=users_email)
        # TODO: ? email sent??
        self.assertFalse(user.is_active)
        # TODO: login not possible?

        # missing rlc key entry added
        self.assertEqual(
            api_models.UserProfile.objects.count() - 2,
            api_models.UsersRlcKeys.objects.count(),
        )  # -2 superuser and forgot password user
        self.assertEqual(1, api_models.MissingRlcKey.objects.count())
        self.assertEqual(user, api_models.MissingRlcKey.objects.first().user)

        # new public, private keys
        self.assertNotEqual(user.get_public_key(), old_public_key)

        # create missing key entries for all records/ delete all current?
        self.assertEqual(
            0, record_models.RecordEncryption.objects.filter(user=user).count()
        )
        self.assertEqual(2, record_models.MissingRecordKey.objects.all().count())

        # login other user of rlc
        client.post(
            "/api/login/",
            {
                "username": self.base_fixtures["users"][0]["user"].email,
                "password": "qwe123",
            },
        )
        self.assertEqual(0, record_models.MissingRecordKey.objects.all().count())
        self.assertEqual(0, api_models.MissingRlcKey.objects.all().count())

        response_from_login_after_reset = client.post(
            "/api/login/", {"username": users_email, "password": "qwe1234"}
        )
        self.assertEqual(200, response_from_login_after_reset.status_code)
        # TODO: superuser rlc encryption_key?

    def test_full_flow_no_encryption_key_of_forgotten_user(self):
        create_missing_key_entries()
        client = APIClient()
        client.post(
            "/api/login/",
            {
                "username": self.base_fixtures["users"][0]["user"].email,
                "password": "qwe123",
            },
        )

        users_email = self.base_fixtures["users"][2]["user"].email
        old_public_key = api_models.UserProfile.objects.get(
            email=users_email
        ).get_public_key()

        client.post("/api/forgot_password/", {"email": users_email})
        self.assertEqual(1, api_models.ForgotPasswordLinks.objects.all().count())
        link = api_models.ForgotPasswordLinks.objects.first()

        response_from_reset = client.post(
            "/api/reset_password/" + link.link + "/", {"new_password": "qwe1234"}
        )
        self.assertEqual(200, response_from_reset.status_code)

        user = api_models.UserProfile.objects.get(email=users_email)
        self.assertFalse(user.is_active)

        # missing rlc key entry added
        self.assertEqual(
            api_models.UserProfile.objects.count() - 2,
            api_models.UsersRlcKeys.objects.count(),
        )  # -2 superuser and forgot password user
        self.assertEqual(1, api_models.MissingRlcKey.objects.count())
        self.assertEqual(user, api_models.MissingRlcKey.objects.first().user)

        # new public, private keys
        self.assertNotEqual(user.get_public_key(), old_public_key)

        # create missing key entries for all records/ delete all current?
        self.assertEqual(
            0, record_models.RecordEncryption.objects.filter(user=user).count()
        )
        self.assertEqual(2, record_models.MissingRecordKey.objects.all().count())

        # mimic error? why is there no user encryption key for this user
        api_models.UserEncryptionKeys.objects.filter(user=user).delete()
        # mimic error, double missing rlc keys entries
        missing_rlc_key_1 = api_models.MissingRlcKey(user=user)
        missing_rlc_key_1.save()
        missing_rlc_key_2 = api_models.MissingRlcKey(user=user)
        missing_rlc_key_2.save()

        # login other user of rlc
        response_from_other_user = client.post(
            "/api/login/",
            {
                "username": self.base_fixtures["users"][0]["user"].email,
                "password": "qwe123",
            },
        )
        self.assertEqual(200, response_from_other_user.status_code)

        # check if user can login again with new password
        response_from_login_after_reset = client.post(
            "/api/login/", {"username": users_email, "password": "qwe1234"}
        )
        self.assertEqual(200, response_from_login_after_reset.status_code)

        # check no missing rlc keys
        self.assertEqual(0, api_models.MissingRlcKey.objects.all().count())
