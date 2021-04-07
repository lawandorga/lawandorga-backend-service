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


class EncryptedRecordDeletionRequestTest(TransactionTestCase):
    def setUp(self):
        self.base_url = "/api/records/record_deletion_requests/"
        self.process_url = "/api/records/process_record_deletion_request/"

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

    def add_process_record_deletion_requests_permission(self) -> None:
        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_PROCESS_RECORD_DELETION_REQUESTS
        )
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            group_has_permission=self.base_fixtures["groups"][0],
        )
        has_permission.save()

    def add_record_deletion_request_fixtures(
        self,
    ) -> [record_models.EncryptedRecordDeletionRequest]:
        request = record_models.EncryptedRecordDeletionRequest(
            record=self.record_fixtures["records"][0]["record"],
            request_from=self.base_fixtures["users"][0]["user"],
        )
        request.save()

        request1 = record_models.EncryptedRecordDeletionRequest(
            record=self.record_fixtures["records"][1]["record"],
            request_from=self.base_fixtures["users"][0]["user"],
        )
        request1.save()

        request2 = record_models.EncryptedRecordDeletionRequest(
            record=self.record_fixtures["records"][0]["record"],
            request_from=self.base_fixtures["users"][1]["user"],
        )
        request2.save()
        return [request, request1, request2]

    def test_record_deletion_request_unauthenticated(self):
        response: Response = APIClient().post(
            self.base_url,
            {"record_id": self.record_fixtures["records"][0]["record"].id},
        )
        self.assertEqual(401, response.status_code)

    def test_record_deletion_request_id_not_found(self):
        response: Response = self.base_fixtures["users"][0]["client"].post(
            self.base_url, {"record_id": 12312}
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__ID_NOT_FOUND["error_code"],
            response.data["error_code"],
        )

    def test_record_deletion_request_no_view_records_permission(self):
        response: Response = self.base_fixtures["users"][3]["client"].post(
            self.base_url,
            {"record_id": self.record_fixtures["records"][0]["record"].id},
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__PERMISSION__INSUFFICIENT["error_code"],
            response.data["error_code"],
        )

    def test_record_deletion_request_foreign_rlc(self):
        foreign_rlc_fixtures = CreateFixtures.create_foreign_rlc_fixture()
        user = foreign_rlc_fixtures["users"][0]["user"]

        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_VIEW_RECORDS_RLC
        )
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            permission_for_rlc=foreign_rlc_fixtures["rlc"],
            user_has_permission=user,
        )
        has_permission.save()

        response: Response = foreign_rlc_fixtures["users"][0]["client"].post(
            self.base_url,
            {"record_id": self.record_fixtures["records"][0]["record"].id},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__WRONG_RLC["error_code"], response.data["error_code"]
        )

    def test_record_deletion_request_no_record_permission(self):
        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_VIEW_RECORDS_RLC
        )
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            user_has_permission=self.base_fixtures["users"][3]["user"],
        )
        has_permission.save()

        response: Response = self.base_fixtures["users"][3]["client"].post(
            self.base_url,
            {"record_id": self.record_fixtures["records"][0]["record"].id},
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__PERMISSION__INSUFFICIENT["error_code"],
            response.data["error_code"],
        )

    def test_record_deletion_request_without_explanation(self):
        deletion_requests_before: (
            int
        ) = record_models.EncryptedRecordDeletionRequest.objects.count()

        response: Response = self.client.post(
            self.base_url,
            {"record_id": self.record_fixtures["records"][0]["record"].id},
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            deletion_requests_before + 1,
            record_models.EncryptedRecordDeletionRequest.objects.count(),
        )
        self.assertEqual(
            self.record_fixtures["records"][0]["record"].id,
            response.data["record"]["id"],
        )
        self.assertEqual(
            "re", response.data["state"],
        )

        deletion_request_from_db: (
            record_models.EncryptedRecordDeletionRequest
        ) = record_models.EncryptedRecordDeletionRequest.objects.get(
            pk=response.data["id"]
        )
        self.assertEqual("", deletion_request_from_db.explanation)
        self.assertEqual(
            self.record_fixtures["records"][0]["record"].id,
            deletion_request_from_db.record.id,
        )

    def test_record_deletion_request_with_explanation(self):
        deletion_requests_before: int = record_models.EncryptedRecordDeletionRequest.objects.count()

        explanation = "i dont want to have this record here"
        response: Response = self.base_fixtures["users"][2]["client"].post(
            self.base_url,
            {
                "record_id": self.record_fixtures["records"][0]["record"].id,
                "explanation": explanation,
            },
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            deletion_requests_before + 1,
            record_models.EncryptedRecordDeletionRequest.objects.count(),
        )
        self.assertEqual(
            self.record_fixtures["records"][0]["record"].id,
            response.data["record"]["id"],
        )

        deletion_request_from_db: (
            record_models.EncryptedRecordDeletionRequest
        ) = record_models.EncryptedRecordDeletionRequest.objects.get(
            pk=response.data["id"]
        )
        self.assertEqual(explanation, deletion_request_from_db.explanation)

    def test_record_deletion_request_second_same_user(self):
        self.add_process_record_deletion_requests_permission()

        deletion_requests_before: int = record_models.EncryptedRecordDeletionRequest.objects.count()
        notification_groups_before: int = api_models.NotificationGroup.objects.count()
        notifications_before: int = api_models.Notification.objects.count()

        response: Response = self.client.post(
            self.base_url,
            {"record_id": self.record_fixtures["records"][0]["record"].id},
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            deletion_requests_before + 1,
            record_models.EncryptedRecordDeletionRequest.objects.count(),
        )
        self.assertEqual(
            notifications_before + 1, api_models.Notification.objects.count()
        )
        self.assertEqual(
            notification_groups_before + 1, api_models.NotificationGroup.objects.count()
        )

        response: Response = self.client.post(
            self.base_url,
            {"record_id": self.record_fixtures["records"][0]["record"].id},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__ALREADY_REQUESTED["error_code"],
            response.data["error_code"],
        )
        self.assertEqual(
            deletion_requests_before + 1,
            record_models.EncryptedRecordDeletionRequest.objects.count(),
        )
        self.assertEqual(
            notifications_before + 1, api_models.Notification.objects.count()
        )
        self.assertEqual(
            notification_groups_before + 1, api_models.NotificationGroup.objects.count()
        )

    def test_record_deletion_request_second_other_user(self):
        self.add_process_record_deletion_requests_permission()

        deletion_requests_before: int = record_models.EncryptedRecordDeletionRequest.objects.count()
        notification_groups_before: int = api_models.NotificationGroup.objects.count()
        notifications_before: int = api_models.Notification.objects.count()

        response: Response = self.client.post(
            self.base_url,
            {"record_id": self.record_fixtures["records"][0]["record"].id},
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            deletion_requests_before + 1,
            record_models.EncryptedRecordDeletionRequest.objects.count(),
        )
        self.assertEqual(
            notifications_before + 1, api_models.Notification.objects.count()
        )
        self.assertEqual(
            notification_groups_before + 1, api_models.NotificationGroup.objects.count()
        )

        response: Response = self.base_fixtures["users"][2]["client"].post(
            self.base_url,
            {"record_id": self.record_fixtures["records"][0]["record"].id},
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            deletion_requests_before + 2,
            record_models.EncryptedRecordDeletionRequest.objects.count(),
        )
        self.assertEqual(
            notifications_before + 3, api_models.Notification.objects.count()
        )
        self.assertEqual(
            notification_groups_before + 2, api_models.NotificationGroup.objects.count()
        )

    def test_get_record_deletion_requests(self):
        response: Response = self.client.get(self.base_url)
        self.assertEqual(403, response.status_code)

        self.add_process_record_deletion_requests_permission()
        record_deletion_requests: [
            record_models.EncryptedRecordDeletionRequest
        ] = self.add_record_deletion_request_fixtures()

        response: Response = self.client.get(self.base_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(response.data))
        self.assertEqual(record_deletion_requests[0].id, response.data[0]["id"])

    def test_process_deletion_no_id(self):
        self.add_process_record_deletion_requests_permission()

        response: Response = self.client.post(self.process_url)
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__ID_NOT_PROVIDED["error_code"],
            response.data["error_code"],
        )

    def test_process_deletion_no_permission(self):
        record_deletion_requests: [
            record_models.EncryptedRecordDeletionRequest
        ] = self.add_record_deletion_request_fixtures()

        response: Response = self.client.post(
            self.process_url,
            {"request_id": record_deletion_requests[1].id, "action": "accept"},
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__PERMISSION__INSUFFICIENT["error_code"],
            response.data["error_code"],
        )

    def test_process_deletion_wrong_id(self):
        self.add_process_record_deletion_requests_permission()
        self.add_record_deletion_request_fixtures()

        response: Response = self.client.post(self.process_url, {"request_id": 123213})
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__ID_NOT_FOUND["error_code"],
            response.data["error_code"],
        )

    def test_process_deletion_no_action(self):
        self.add_process_record_deletion_requests_permission()
        record_deletion_requests: [
            record_models.EncryptedRecordDeletionRequest
        ] = self.add_record_deletion_request_fixtures()

        response: Response = self.client.post(
            self.process_url, {"request_id": record_deletion_requests[0].id}
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__NO_ACTION_PROVIDED["error_code"],
            response.data["error_code"],
        )

    def test_process_deletion_action_not_valid(self):
        self.add_process_record_deletion_requests_permission()
        record_deletion_requests: [
            record_models.EncryptedRecordDeletionRequest
        ] = self.add_record_deletion_request_fixtures()

        response: Response = self.client.post(
            self.process_url,
            {"request_id": record_deletion_requests[0].id, "action": "something"},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__ACTION_NOT_VALID["error_code"],
            response.data["error_code"],
        )

    def test_accept_deletion_request(self):
        self.add_process_record_deletion_requests_permission()
        record_deletion_requests: [
            record_models.EncryptedRecordDeletionRequest
        ] = self.add_record_deletion_request_fixtures()
        number_of_records_before: int = record_models.EncryptedRecord.objects.count()
        number_of_notifications_before: int = api_models.Notification.objects.count()
        number_of_notification_groups_before: int = api_models.NotificationGroup.objects.count()

        response: Response = self.client.post(
            self.process_url,
            {"request_id": record_deletion_requests[1].id, "action": "accept"},
        )
        self.assertEqual(200, response.status_code)
        deletion_request_from_db: (
            record_models.EncryptedRecordDeletionRequest
        ) = record_models.EncryptedRecordDeletionRequest.objects.get(
            pk=record_deletion_requests[1].id
        )
        self.assertEqual("gr", deletion_request_from_db.state)
        self.assertEqual(
            0,
            record_models.EncryptedRecord.objects.filter(
                pk=record_deletion_requests[1].record.id
            ).count(),
        )
        self.assertEqual(
            number_of_records_before - 1, record_models.EncryptedRecord.objects.count()
        )
        self.assertEqual(
            2,
            record_models.EncryptedRecordDeletionRequest.objects.filter(
                state="re"
            ).count(),
        )
        self.assertEqual(
            1,
            record_models.EncryptedRecordDeletionRequest.objects.filter(
                state="gr"
            ).count(),
        )
        self.assertEqual(
            number_of_notification_groups_before + 3,
            api_models.NotificationGroup.objects.count(),
        )
        self.assertEqual(
            number_of_notifications_before + 3, api_models.Notification.objects.count()
        )

    def test_accept_doubled_deletion_request(self):
        self.add_process_record_deletion_requests_permission()
        record_deletion_requests: [
            record_models.EncryptedRecordDeletionRequest
        ] = self.add_record_deletion_request_fixtures()
        number_of_records_before: int = record_models.EncryptedRecord.objects.count()
        number_of_notifications_before: int = api_models.Notification.objects.count()
        number_of_notification_groups_before: int = api_models.NotificationGroup.objects.count()

        response: Response = self.client.post(
            self.process_url,
            {"request_id": record_deletion_requests[0].id, "action": "accept"},
        )
        self.assertEqual(200, response.status_code)
        deletion_request_from_db: (
            record_models.EncryptedRecordDeletionRequest
        ) = record_models.EncryptedRecordDeletionRequest.objects.get(
            pk=record_deletion_requests[0].id
        )
        self.assertEqual("gr", deletion_request_from_db.state)
        self.assertEqual(
            0,
            record_models.EncryptedRecord.objects.filter(
                pk=record_deletion_requests[0].record.id
            ).count(),
        )
        self.assertEqual(
            number_of_records_before - 1, record_models.EncryptedRecord.objects.count()
        )
        self.assertEqual(
            1,
            record_models.EncryptedRecordDeletionRequest.objects.filter(
                state="re"
            ).count(),
        )
        self.assertEqual(
            2,
            record_models.EncryptedRecordDeletionRequest.objects.filter(
                state="gr"
            ).count(),
        )
        self.assertEqual(
            number_of_notification_groups_before + 3,
            api_models.NotificationGroup.objects.count(),
        )
        self.assertEqual(
            number_of_notifications_before + 3, api_models.Notification.objects.count()
        )

    def test_decline_deletion_request(self):
        self.add_process_record_deletion_requests_permission()
        record_deletion_requests: [
            record_models.EncryptedRecordDeletionRequest
        ] = self.add_record_deletion_request_fixtures()
        number_of_records_before: int = record_models.EncryptedRecord.objects.count()
        number_of_notifications_before: int = api_models.Notification.objects.count()
        number_of_notification_groups_before: int = api_models.NotificationGroup.objects.count()

        response: Response = self.client.post(
            self.process_url,
            {"request_id": record_deletion_requests[0].id, "action": "decline"},
        )
        self.assertEqual(200, response.status_code)
        deletion_request_from_db: (
            record_models.EncryptedRecordDeletionRequest
        ) = record_models.EncryptedRecordDeletionRequest.objects.get(
            pk=record_deletion_requests[0].id
        )
        self.assertEqual("de", deletion_request_from_db.state)
        self.assertEqual(
            1,
            record_models.EncryptedRecord.objects.filter(
                pk=record_deletion_requests[0].record.id
            ).count(),
        )
        self.assertEqual(
            number_of_records_before, record_models.EncryptedRecord.objects.count()
        )
        self.assertEqual(
            2,
            record_models.EncryptedRecordDeletionRequest.objects.filter(
                state="re"
            ).count(),
        )
        self.assertEqual(
            1,
            record_models.EncryptedRecordDeletionRequest.objects.filter(
                state="de"
            ).count(),
        )
        self.assertEqual(
            number_of_notification_groups_before + 2,
            api_models.NotificationGroup.objects.count(),
        )
        self.assertEqual(
            number_of_notifications_before + 2, api_models.Notification.objects.count()
        )

    def test_double_process_request(self):
        self.add_process_record_deletion_requests_permission()
        record_deletion_requests: [
            record_models.EncryptedRecordDeletionRequest
        ] = self.add_record_deletion_request_fixtures()
        record_deletion_requests[0].state = "de"
        record_deletion_requests[0].save()
        number_of_notifications_before: int = api_models.Notification.objects.count()
        number_of_notification_groups_before: int = api_models.NotificationGroup.objects.count()

        response: Response = self.client.post(
            self.process_url,
            {"request_id": record_deletion_requests[0].id, "action": "accept"},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__ALREADY_PROCESSED["error_code"],
            response.data["error_code"],
        )
        self.assertEqual(
            number_of_notification_groups_before,
            api_models.NotificationGroup.objects.count(),
        )
        self.assertEqual(
            number_of_notifications_before, api_models.Notification.objects.count()
        )

    def test_process_record_deletion_foreign_rlc(self):
        foreign_rlc_fixtures = CreateFixtures.create_foreign_rlc_fixture()
        user = foreign_rlc_fixtures["users"][0]["user"]
        record_deletion_requests: [
            record_models.EncryptedRecordDeletionRequest
        ] = self.add_record_deletion_request_fixtures()

        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_VIEW_RECORDS_RLC
        )
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            permission_for_rlc=foreign_rlc_fixtures["rlc"],
            user_has_permission=user,
        )
        has_permission.save()
        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_PROCESS_RECORD_DELETION_REQUESTS
        )
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            permission_for_rlc=foreign_rlc_fixtures["rlc"],
            user_has_permission=user,
        )
        has_permission.save()

        response: Response = foreign_rlc_fixtures["users"][0]["client"].post(
            self.process_url,
            {"request_id": record_deletion_requests[0].id, "action": "accept"},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__WRONG_RLC["error_code"], response.data["error_code"]
        )
