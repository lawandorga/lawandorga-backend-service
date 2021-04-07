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
    PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC,
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
        self.request_client: APIClient = self.base_fixtures["users"][3]["client"]
        self.request_user: api_models.UserProfile = self.base_fixtures["users"][3][
            "user"
        ]
        self.request_private: bytes = self.base_fixtures["users"][3]["private"]
        self.process_client: APIClient = self.base_fixtures["users"][0]["client"]
        self.process_user: api_models.UserProfile = self.base_fixtures["users"][0][
            "user"
        ]
        self.process_private: bytes = self.base_fixtures["users"][0]["private"]

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

    def add_process_record_permission_request_permission(self) -> None:
        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC
        )
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            group_has_permission=self.base_fixtures["groups"][0],
        )
        has_permission.save()

    def add_record_permission_request_fixtures(
        self,
    ) -> [record_models.EncryptedRecordPermission]:
        """
        creates two example requests from user, one declined, one still requested
        :return:
        """
        permission1: record_models.EncryptedRecordPermission = record_models.EncryptedRecordPermission(
            request_from=self.request_user,
            record=self.record_fixtures["records"][0]["record"],
            state="de",
        )
        permission1.save()

        permission2: record_models.EncryptedRecordPermission = record_models.EncryptedRecordPermission(
            request_from=self.request_user,
            record=self.record_fixtures["records"][0]["record"],
            state="re",
        )
        permission2.save()

        return [permission1, permission2]

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

        response: Response = self.request_client.post(url, {})
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__ID_NOT_FOUND["error_code"],
            response.data["error_code"],
        )

    def test_request_record_permission_no_id(self):
        url = self.base_request_url + "a" + self.trailing_request_url

        response: Response = self.request_client.post(url, {})
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__ID_NOT_FOUND["error_code"],
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
        self.add_process_record_permission_request_permission()
        url = (
            self.base_request_url
            + str(self.record_fixtures["records"][0]["record"].id)
            + self.trailing_request_url
        )
        record_permission_requests_before: int = record_models.EncryptedRecordPermission.objects.count()
        notification_groups_before: int = api_models.NotificationGroup.objects.count()
        notifications_before: int = api_models.Notification.objects.count()

        response: Response = self.request_client.post(url, {})
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
        self.assertEqual(self.request_user, request_from_db.request_from)
        self.assertEqual(
            notification_groups_before + 2, api_models.NotificationGroup.objects.count()
        )
        self.assertEqual(
            notifications_before + 2, api_models.Notification.objects.count()
        )
        self.assertEqual(
            2,
            api_models.Notification.objects.filter(
                type=api_models.NotificationType.RECORD_PERMISSION_REQUEST__REQUESTED.value
            ).count(),
        )

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
            request_from=self.request_user,
            record=self.record_fixtures["records"][0]["record"],
            state="re",
        )
        permission.save()

        response: Response = self.request_client.post(url, {})
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
            request_from=self.request_user,
            record=self.record_fixtures["records"][0]["record"],
            state="de",
        )
        permission.save()
        record_permission_requests_before: int = record_models.EncryptedRecordPermission.objects.count()

        response: Response = self.request_client.post(url, {})
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
        self.assertEqual(self.request_user, request_from_db.request_from)

    def test_accept_record_permission(self):
        self.add_process_record_permission_request_permission()
        requests: [
            record_models.EncryptedRecordPermission
        ] = self.add_record_permission_request_fixtures()
        record_encryptions_before = record_models.RecordEncryption.objects.count()

        response: Response = self.process_client.post(
            self.list_and_process_url,
            {"id": requests[1].id, "action": "accept"},
            format="json",
            **{"HTTP_PRIVATE_KEY": self.process_private},
        )

        self.assertEqual(200, response.status_code)
        request_from_db: (
            record_models.EncryptedRecordPermission
        ) = record_models.EncryptedRecordPermission.objects.get(id=response.data["id"])
        self.assertEqual("gr", request_from_db.state)
        self.assertEqual(requests[1].record, request_from_db.record)

        self.assertEqual(
            record_encryptions_before + 1,
            record_models.RecordEncryption.objects.count(),
        )

        self.assertEqual(4, api_models.Notification.objects.count())
        self.assertEqual(4, api_models.NotificationGroup.objects.count())

    def test_decline_record_permission(self):
        self.add_process_record_permission_request_permission()
        requests: [
            record_models.EncryptedRecordPermission
        ] = self.add_record_permission_request_fixtures()
        record_encryptions_before: int = record_models.RecordEncryption.objects.count()

        response: Response = self.process_client.post(
            self.list_and_process_url,
            {"id": requests[1].id, "action": "decline"},
            format="json",
            **{"HTTP_PRIVATE_KEY": self.process_private},
        )

        self.assertEqual(200, response.status_code)
        request_from_db: (
            record_models.EncryptedRecordPermission
        ) = record_models.EncryptedRecordPermission.objects.get(id=response.data["id"])
        self.assertEqual("de", request_from_db.state)
        self.assertEqual(requests[1].record, request_from_db.record)
        self.assertEqual(
            record_encryptions_before, record_models.RecordEncryption.objects.count()
        )

    def test_process_record_permission_wrong_id(self):
        self.add_process_record_permission_request_permission()

        response: Response = self.process_client.post(
            self.list_and_process_url,
            {"id": 1123123, "action": "accept"},
            format="json",
            **{"HTTP_PRIVATE_KEY": self.process_private},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__ID_NOT_FOUND["error_code"],
            response.data["error_code"],
        )

    def test_process_record_permission_no_id(self):
        self.add_process_record_permission_request_permission()

        response: Response = self.process_client.post(
            self.list_and_process_url,
            {"action": "accept"},
            format="json",
            **{"HTTP_PRIVATE_KEY": self.process_private},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__ID_NOT_PROVIDED["error_code"],
            response.data["error_code"],
        )

    def test_process_record_permission_no_private_key(self):
        self.add_process_record_permission_request_permission()
        requests: [
            record_models.EncryptedRecordPermission
        ] = self.add_record_permission_request_fixtures()

        response: Response = self.process_client.post(
            self.list_and_process_url,
            {"id": requests[1].id, "action": "accept"},
            format="json",
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__USER__NO_PRIVATE_KEY_PROVIDED["error_code"],
            response.data["error_code"],
        )

    def test_process_record_permission_no_permission(self):
        # self.add_process_record_permission_request_permission()
        requests: [
            record_models.EncryptedRecordPermission
        ] = self.add_record_permission_request_fixtures()

        response: Response = self.process_client.post(
            self.list_and_process_url,
            {"id": requests[1].id, "action": "accept"},
            format="json",
            **{"HTTP_PRIVATE_KEY": self.process_private},
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__PERMISSION__INSUFFICIENT["error_code"],
            response.data["error_code"],
        )

    def test_process_record_permission_wrong_action(self):
        self.add_process_record_permission_request_permission()
        requests: [
            record_models.EncryptedRecordPermission
        ] = self.add_record_permission_request_fixtures()

        response: Response = self.process_client.post(
            self.list_and_process_url,
            {"id": requests[1].id, "action": "somethingelse"},
            format="json",
            **{"HTTP_PRIVATE_KEY": self.process_private},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__ACTION_NOT_VALID["error_code"],
            response.data["error_code"],
        )

    def test_process_record_permission_no_action(self):
        self.add_process_record_permission_request_permission()
        requests: [
            record_models.EncryptedRecordPermission
        ] = self.add_record_permission_request_fixtures()

        response: Response = self.process_client.post(
            self.list_and_process_url,
            {"id": requests[1].id,},
            format="json",
            **{"HTTP_PRIVATE_KEY": self.process_private},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__NO_ACTION_PROVIDED["error_code"],
            response.data["error_code"],
        )

    def test_double_process_record_permission(self):
        self.add_process_record_permission_request_permission()
        requests: [
            record_models.EncryptedRecordPermission
        ] = self.add_record_permission_request_fixtures()

        response: Response = self.process_client.post(
            self.list_and_process_url,
            {"id": requests[0].id, "action": "accept"},
            format="json",
            **{"HTTP_PRIVATE_KEY": self.process_private},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__ALREADY_PROCESSED["error_code"],
            response.data["error_code"],
        )

    def test_process_record_permission_foreign_rlc(self):
        foreign_rlc_fixtures = CreateFixtures.create_foreign_rlc_fixture()
        user = foreign_rlc_fixtures["users"][0]["user"]
        requests: [
            record_models.EncryptedRecordPermission
        ] = self.add_record_permission_request_fixtures()

        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC
        )
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            permission_for_rlc=foreign_rlc_fixtures["rlc"],
            user_has_permission=user,
        )
        has_permission.save()

        response: Response = foreign_rlc_fixtures["users"][0]["client"].post(
            self.list_and_process_url,
            {"id": requests[1].id, "action": "accept"},
            format="json",
            **{"HTTP_PRIVATE_KEY": foreign_rlc_fixtures["users"][0]["private"]},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__WRONG_RLC["error_code"],
            response.data["error_code"],
        )

    def test_list_record_permissions(self):
        self.add_process_record_permission_request_permission()
        response: Response = self.process_client.get(self.list_and_process_url)

        self.assertEqual(200, response.status_code)
        self.assertEqual(2, response.data.__len__())

    def test_list_record_permissions_foreign_rlc(self):
        pass

    def test_list_record_permissions_no_permission(self):
        response: Response = self.process_client.get(self.list_and_process_url)

        self.assertEqual(403, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__PERMISSION__INSUFFICIENT["error_code"],
            response.data["error_code"],
        )

    def test_list_record_permissions_unauthenticated(self):
        client: APIClient = APIClient()
        response: Response = client.get(self.list_and_process_url)

        self.assertEqual(401, response.status_code)
        self.assertEqual(
            "not_authenticated", response.data["error_code"],
        )
