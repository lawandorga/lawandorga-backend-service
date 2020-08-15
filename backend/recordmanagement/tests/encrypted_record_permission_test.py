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
        self.client: APIClient = self.base_fixtures["users"][0]["client"]
        self.user: api_models.UserProfile = self.base_fixtures["users"][0]["user"]

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
            group_has_permission=self.base_fixtures["groups"][1],
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

    # TODO: from other rlc

    def test_request_record_permission_no_id(self):
        url = self.base_request_url + "a" + self.trailing_request_url

        response: Response = self.client.post(url, {})
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__RECORD__RECORD__NOT_EXISTING["error_code"],
            response.data["error_code"],
        )

    # TODO
    # send request
    # success
    # wrong rlc
    # without access to records
    # 1: already has access
    # 1: second request same record/ doubled (other is still requested)
    # 1: doubled (other is declined)

    # process request
    # success
    # wrong id
    # no process permission
    # no action
    # wrong action
    # already processed/ doubled

    # get requests
