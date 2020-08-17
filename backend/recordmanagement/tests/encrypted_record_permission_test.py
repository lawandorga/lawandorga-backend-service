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
from backend.recordmanagement import models as record_models
from backend.static.permissions import (
    PERMISSION_VIEW_RECORDS_RLC,
    PERMISSION_PROCESS_RECORD_DELETION_REQUESTS,
)
from backend.static import error_codes


class EncryptedRecordRequestTest(TransactionTestCase):
    def setUp(self):
        # record/(?P<id>.+)/request_permission$
        self.base_request_url = "/api/records/record/"
        self.trailing_request_url = "/request_permission"
        self.list_and_process_url = "/api/records/e_record_permission_requests/"

        self.base_fixtures = CreateFixtures.create_base_fixtures()
        users: [api_models.UserProfile] = [
            self.base_fixtures["users"][0]["user"],
            self.base_fixtures["users"][1]["user"],
            self.base_fixtures["users"][2]["user"],
        ]
        self.record_fixtures = CreateFixtures.create_record_base_fixtures(
            rlc=self.base_fixtures["rlc"], users=users
        )
        self.client: APIClient = self.base_fixtures["users"][3]["client"]
        self.user: api_models.UserProfile = self.base_fixtures["users"][3]["user"]

        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_VIEW_RECORDS_RLC
        )
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            group_has_permission=self.base_fixtures["groups"][0],
        )
        has_permission.save()
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            group_has_permission=self.base_fixtures["groups"][2],
        )
        has_permission.save()

    # def add_process_record_deletion_requests_permission(self) -> None:
    #     permission: api_models.Permission = api_models.Permission.objects.get(
    #         name=PERMISSION_PROCESS_RECORD_DELETION_REQUESTS
    #     )
    #     has_permission: api_models.HasPermission = api_models.HasPermission(
    #         permission=permission,
    #         permission_for_rlc=self.base_fixtures["rlc"],
    #         group_has_permission=self.base_fixtures["groups"][0],
    #     )
    #     has_permission.save()
    #
    # def add_record_deletion_request_fixtures(
    #     self,
    # ) -> [record_models.EncryptedRecordDeletionRequest]:
    #     request = record_models.EncryptedRecordDeletionRequest(
    #         record=self.record_fixtures["records"][0]["record"],
    #         request_from=self.base_fixtures["users"][0]["user"],
    #     )
    #     request.save()
    #
    #     request1 = record_models.EncryptedRecordDeletionRequest(
    #         record=self.record_fixtures["records"][1]["record"],
    #         request_from=self.base_fixtures["users"][0]["user"],
    #     )
    #     request1.save()
    #
    #     request2 = record_models.EncryptedRecordDeletionRequest(
    #         record=self.record_fixtures["records"][0]["record"],
    #         request_from=self.base_fixtures["users"][1]["user"],
    #     )
    #     request2.save()
    #     return [request, request1, request2]

    def test_request_record_permission_unauthenticated(self):
        client = APIClient()
        url = (
            self.base_request_url
            + str(self.record_fixtures["records"][0]["record"].id)
            + self.trailing_request_url
        )

        response: Response = client.post(url, {})
        self.assertEqual(401, response.status_code)

    def test_request_record_permission_wrong_id(self):
        url = self.base_request_url + str(12983129) + self.trailing_request_url

        response: Response = self.client.post(url, {})
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__RECORD__RECORD__NOT_EXISTING["error_code"],
            response.data["error_code"],
        )

    def test_request_record_permission_no_id(self):
        url = self.base_request_url + "a" + self.trailing_request_url

        response: Response = self.client.post(url, {})
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__RECORD__RECORD__NOT_EXISTING["error_code"],
            response.data["error_code"],
        )

    def test_request_record_permission_foreign_rlc(self):
        foreign_rlc_fixtures = CreateFixtures.create_foreign_rlc_fixture()
        user = foreign_rlc_fixtures["users"][0]["user"]
        url = (
            self.base_request_url
            + str(self.record_fixtures["records"][0]["record"].id)
            + self.trailing_request_url
        )
        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_VIEW_RECORDS_RLC
        )
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            permission_for_rlc=foreign_rlc_fixtures["rlc"],
            user_has_permission=user,
        )
        has_permission.save()

        record_permission_requests_before: int = record_models.EncryptedRecordPermission.objects.count()

        response: Response = foreign_rlc_fixtures["users"][0]["client"].post(url,)
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__WRONG_RLC["error_code"], response.data["error_code"]
        )
        self.assertEqual(
            record_permission_requests_before,
            record_models.EncryptedRecordPermission.objects.count(),
        )

    def test_request_record_permission_without_record_access(self):
        user: api_models.UserProfile = api_models.UserProfile(
            name="temp user",
            email="tempuser@law-orga.de",
            rlc=self.base_fixtures["rlc"],
        )
        user.set_password("qwe123")
        user.save()
        client = APIClient()
        client.force_authenticate(user=user)

        url = (
            self.base_request_url
            + str(self.record_fixtures["records"][0]["record"].id)
            + self.trailing_request_url
        )
        response: Response = client.post(url, {})
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__PERMISSION__INSUFFICIENT["error_code"],
            response.data["error_code"],
        )

    def test_request_record_permission_success(self):
        url = (
            self.base_request_url
            + str(self.record_fixtures["records"][0]["record"].id)
            + self.trailing_request_url
        )
        record_permission_requests_before: int = record_models.EncryptedRecordPermission.objects.count()

        response: Response = self.client.post(url, {})
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            record_permission_requests_before + 1,
            record_models.EncryptedRecordPermission.objects.count(),
        )
        request_from_db: record_models.EncryptedRecordPermission = record_models.EncryptedRecordPermission.objects.get(
            pk=response.data["id"]
        )
        self.assertEqual(
            self.record_fixtures["records"][0]["record"], request_from_db.record
        )
        self.assertEqual("re", request_from_db.state)
        self.assertEqual(self.user, request_from_db.request_from)

    def test_request_record_permission_doubled_already_working_on(self):
        url = (
            self.base_request_url
            + str(self.record_fixtures["records"][0]["record"].id)
            + self.trailing_request_url
        )

        response: Response = self.base_fixtures["users"][2]["client"].post(url, {})
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__RECORD__PERMISSION__ALREADY_WORKING_ON["error_code"],
            response.data["error_code"],
        )

        response: Response = self.base_fixtures["users"][0]["client"].post(url, {})
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__RECORD__PERMISSION__ALREADY_WORKING_ON["error_code"],
            response.data["error_code"],
        )

    def test_request_record_permission_doubled_still_requested(self):
        url = (
            self.base_request_url
            + str(self.record_fixtures["records"][0]["record"].id)
            + self.trailing_request_url
        )
        permission: record_models.EncryptedRecordPermission = record_models.EncryptedRecordPermission(
            request_from=self.user,
            record=self.record_fixtures["records"][0]["record"],
            state="re",
        )
        permission.save()

        response: Response = self.client.post(url, {})
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__RECORD__PERMISSION__ALREADY_REQUESTED["error_code"],
            response.data["error_code"],
        )

    def test_request_record_permission_doubled_declined_success(self):
        url = (
            self.base_request_url
            + str(self.record_fixtures["records"][0]["record"].id)
            + self.trailing_request_url
        )
        permission: record_models.EncryptedRecordPermission = record_models.EncryptedRecordPermission(
            request_from=self.user,
            record=self.record_fixtures["records"][0]["record"],
            state="de",
        )
        permission.save()
        record_permission_requests_before: int = record_models.EncryptedRecordPermission.objects.count()

        response: Response = self.client.post(url, {})
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            record_permission_requests_before + 1,
            record_models.EncryptedRecordPermission.objects.count(),
        )
        request_from_db: record_models.EncryptedRecordPermission = record_models.EncryptedRecordPermission.objects.get(
            pk=response.data["id"]
        )
        self.assertEqual(
            self.record_fixtures["records"][0]["record"], request_from_db.record
        )
        self.assertEqual("re", request_from_db.state)
        self.assertEqual(self.user, request_from_db.request_from)

    # process request
    # success
    # wrong id
    # no process permission
    # no action
    # wrong action
    # already processed/ doubled

    # get requests
