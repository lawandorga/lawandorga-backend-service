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
from unittest.mock import MagicMock

from django.test import TransactionTestCase
from rest_framework.response import Response
from rest_framework.test import APIClient

from backend.api import models as api_models
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.recordmanagement import models as record_models
from backend.static.encrypted_storage import EncryptedStorage
from backend.static.permissions import (
    PERMISSION_PROCESS_RECORD_DOCUMENT_DELETION_REQUESTS,
    PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC,
)
from backend.static import error_codes


class EncryptedRecordDocumentDeletionRequestTest(TransactionTestCase):
    def setUp(self):
        self.base_url = "/api/records/record_document_deletion_requests/"
        self.process_url = "/api/records/process_record_document_deletion_request/"

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

    def add_process_record_document_deletion_requests_permission(self):
        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_PROCESS_RECORD_DOCUMENT_DELETION_REQUESTS
        )
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            group_has_permission=self.base_fixtures["groups"][0],
        )
        has_permission.save()

    def add_record_document_deletion_requests_fixtures(
        self,
    ) -> [record_models.EncryptedRecordDocumentDeletionRequest]:
        documents: [record_models.EncryptedRecordDocument] = list(
            record_models.EncryptedRecordDocument.objects.all()
        )
        request: (
            record_models.EncryptedRecordDocumentDeletionRequest
        ) = record_models.EncryptedRecordDocumentDeletionRequest(
            request_from=self.base_fixtures["users"][1]["user"],
            document=documents[0],
            record=documents[0].record,
        )
        request.save()
        request2: (
            record_models.EncryptedRecordDocumentDeletionRequest
        ) = record_models.EncryptedRecordDocumentDeletionRequest(
            request_from=self.base_fixtures["users"][0]["user"],
            document=documents[0],
            record=documents[0].record,
        )
        request2.save()
        request1: (
            record_models.EncryptedRecordDocumentDeletionRequest
        ) = record_models.EncryptedRecordDocumentDeletionRequest(
            request_from=self.base_fixtures["users"][0]["user"],
            document=documents[1],
            record=documents[1].record,
        )
        request1.save()

        return [request, request2, request1]

    def test_record_document_deletion_requested_unauthenticated(self):
        client: APIClient = APIClient()
        document = record_models.EncryptedRecordDocument.objects.first()

        response: Response = client.post(self.base_url, {"document_id": document.id})
        self.assertEqual(401, response.status_code)

    def test_record_document_deletion_requested_no_permission(self):
        document = record_models.EncryptedRecordDocument.objects.first()

        response: Response = self.base_fixtures["users"][3]["client"].post(
            self.base_url, {"document_id": document.id}
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__PERMISSION__INSUFFICIENT["error_code"],
            response.data["error_code"],
        )

    def test_record_document_deletion_requested_success_full_detail_all_records_permission(
        self,
    ):
        user: api_models.UserProfile = self.base_fixtures["users"][3]["user"]
        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC
        )
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            user_has_permission=user,
        )
        has_permission.save()

        self.assertEqual(
            0, record_models.EncryptedRecordDocumentDeletionRequest.objects.count()
        )
        document = record_models.EncryptedRecordDocument.objects.first()

        response: Response = self.base_fixtures["users"][3]["client"].post(
            self.base_url, {"document_id": document.id}
        )
        self.assertEqual(201, response.status_code)

    def test_record_document_deletion_requested_success(self):
        self.assertEqual(
            0, record_models.EncryptedRecordDocumentDeletionRequest.objects.count()
        )
        document = record_models.EncryptedRecordDocument.objects.first()

        response: Response = self.client.post(
            self.base_url, {"document_id": document.id}
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            1, record_models.EncryptedRecordDocumentDeletionRequest.objects.count()
        )
        newly_created_deletion_request: (
            record_models.EncryptedRecordDocumentDeletionRequest
        ) = record_models.EncryptedRecordDocumentDeletionRequest.objects.first()
        self.assertEqual(
            newly_created_deletion_request.document.record,
            self.record_fixtures["records"][0]["record"],
        )
        self.assertEqual("re", newly_created_deletion_request.state)
        self.assertEqual(self.user, newly_created_deletion_request.request_from)
        # TODO: copy in notifications and check if notifications are there

    def test_record_document_deletion_requested_success_with_explanation(self):
        self.assertEqual(
            0, record_models.EncryptedRecordDocumentDeletionRequest.objects.count()
        )
        document = record_models.EncryptedRecordDocument.objects.first()

        explanation = "was a mistake to upload this, some private pictures"
        response: Response = self.client.post(
            self.base_url, {"document_id": document.id, "explanation": explanation}
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            1, record_models.EncryptedRecordDocumentDeletionRequest.objects.count()
        )
        newly_created_deletion_request: (
            record_models.EncryptedRecordDocumentDeletionRequest
        ) = record_models.EncryptedRecordDocumentDeletionRequest.objects.first()
        self.assertEqual(
            newly_created_deletion_request.document.record,
            self.record_fixtures["records"][0]["record"],
        )
        self.assertEqual(explanation, newly_created_deletion_request.explanation)

    def test_record_document_deletion_requested_foreign_rlc(self):
        foreign_rlc_fixtures = CreateFixtures.create_foreign_rlc_fixture()
        user = foreign_rlc_fixtures["users"][0]["user"]

        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC
        )
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            permission_for_rlc=foreign_rlc_fixtures["rlc"],
            user_has_permission=user,
        )
        has_permission.save()
        document = record_models.EncryptedRecordDocument.objects.first()

        response: Response = foreign_rlc_fixtures["users"][0]["client"].post(
            self.base_url, {"document_id": document.id}
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__PERMISSION__INSUFFICIENT["error_code"],
            response.data["error_code"],
        )

    def test_record_document_deletion_requested_wrong_id(self):
        self.assertEqual(
            0, record_models.EncryptedRecordDocumentDeletionRequest.objects.count()
        )

        response: Response = self.client.post(self.base_url, {"document_id": 243234})
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__ID_NOT_FOUND["error_code"],
            response.data["error_code"],
        )

    def test_record_document_deletion_requested_doubled_same_user(self):
        self.assertEqual(
            0, record_models.EncryptedRecordDocumentDeletionRequest.objects.count()
        )
        document = record_models.EncryptedRecordDocument.objects.first()

        response: Response = self.client.post(
            self.base_url, {"document_id": document.id}
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            1, record_models.EncryptedRecordDocumentDeletionRequest.objects.count()
        )

        response: Response = self.client.post(
            self.base_url, {"document_id": document.id}
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__ALREADY_REQUESTED["error_code"],
            response.data["error_code"],
        )

    def test_record_document_deletion_requested_doubled_other_user(self):
        self.assertEqual(
            0, record_models.EncryptedRecordDocumentDeletionRequest.objects.count()
        )
        document = record_models.EncryptedRecordDocument.objects.first()

        response: Response = self.client.post(
            self.base_url, {"document_id": document.id}
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            1, record_models.EncryptedRecordDocumentDeletionRequest.objects.count()
        )

        response: Response = self.base_fixtures["users"][1]["client"].post(
            self.base_url, {"document_id": document.id}
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            2, record_models.EncryptedRecordDocumentDeletionRequest.objects.count()
        )

    def test_record_document_deletion_list_no_permission(self):
        response: Response = self.client.get(self.base_url)
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__PERMISSION__INSUFFICIENT["error_code"],
            response.data["error_code"],
        )

    def test_record_document_deletion_list_success(self):
        self.add_record_document_deletion_requests_fixtures()
        self.assertEqual(
            3, record_models.EncryptedRecordDocumentDeletionRequest.objects.count()
        )
        self.add_process_record_document_deletion_requests_permission()

        response: Response = self.client.get(self.base_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, response.data.__len__())

    def test_record_document_deletion_list_unauthenticated(self):
        response: Response = APIClient().get(self.base_url)
        self.assertEqual(401, response.status_code)

    def test_record_document_deletion_list_foreign_rlc(self):
        foreign_rlc_fixtures = CreateFixtures.create_foreign_rlc_fixture()
        user = foreign_rlc_fixtures["users"][0]["user"]
        self.add_record_document_deletion_requests_fixtures()

        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_PROCESS_RECORD_DOCUMENT_DELETION_REQUESTS
        )
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            permission_for_rlc=foreign_rlc_fixtures["rlc"],
            user_has_permission=user,
        )
        has_permission.save()

        response: Response = foreign_rlc_fixtures["users"][0]["client"].get(
            self.base_url
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, response.data.__len__())

    def test_accept_record_document_deletion_request(self):
        EncryptedStorage.delete_on_s3 = MagicMock()
        deletion_requests: [
            record_models.EncryptedRecordDocumentDeletionRequest
        ] = self.add_record_document_deletion_requests_fixtures()
        self.add_process_record_document_deletion_requests_permission()
        number_of_record_documents_before: int = record_models.EncryptedRecordDocument.objects.count()

        response: Response = self.client.post(
            self.process_url,
            {"request_id": deletion_requests[2].id, "action": "accept"},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            number_of_record_documents_before - 1,
            record_models.EncryptedRecordDocument.objects.count(),
        )
        self.assertEqual(1, EncryptedStorage.delete_on_s3.call_count)
        request_from_db: (
            record_models.EncryptedRecordDocumentDeletionRequest
        ) = record_models.EncryptedRecordDocumentDeletionRequest.objects.get(
            pk=deletion_requests[2].id
        )
        self.assertEqual("ac", request_from_db.state)
        self.assertEqual(
            2,
            record_models.EncryptedRecordDocumentDeletionRequest.objects.filter(
                state="re"
            ).count(),
        )
        self.assertEqual(
            1,
            record_models.EncryptedRecordDocumentDeletionRequest.objects.filter(
                state="ac"
            ).count(),
        )

    def test_accept_record_document_deletion_request_multiple(self):
        EncryptedStorage.delete_on_s3 = MagicMock()
        deletion_requests: [
            record_models.EncryptedRecordDocumentDeletionRequest
        ] = self.add_record_document_deletion_requests_fixtures()
        self.add_process_record_document_deletion_requests_permission()
        number_of_record_documents_before: int = record_models.EncryptedRecordDocument.objects.count()

        # there are 2 deletion requests for same document
        # accept one, other should be accepted too
        response: Response = self.client.post(
            self.process_url,
            {"request_id": deletion_requests[0].id, "action": "accept"},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            number_of_record_documents_before - 1,
            record_models.EncryptedRecordDocument.objects.count(),
        )
        self.assertEqual(1, EncryptedStorage.delete_on_s3.call_count)
        request_from_db: (
            record_models.EncryptedRecordDocumentDeletionRequest
        ) = record_models.EncryptedRecordDocumentDeletionRequest.objects.get(
            pk=deletion_requests[0].id
        )
        self.assertEqual("ac", request_from_db.state)
        self.assertEqual(
            1,
            record_models.EncryptedRecordDocumentDeletionRequest.objects.filter(
                state="re"
            ).count(),
        )
        self.assertEqual(
            2,
            record_models.EncryptedRecordDocumentDeletionRequest.objects.filter(
                state="ac"
            ).count(),
        )

    def test_decline_record_document_deletion_request(self):
        EncryptedStorage.delete_on_s3 = MagicMock()
        deletion_requests: [
            record_models.EncryptedRecordDocumentDeletionRequest
        ] = self.add_record_document_deletion_requests_fixtures()
        self.add_process_record_document_deletion_requests_permission()
        number_of_record_documents_before: int = record_models.EncryptedRecordDocument.objects.count()

        response: Response = self.client.post(
            self.process_url,
            {"request_id": deletion_requests[2].id, "action": "decline"},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            number_of_record_documents_before,
            record_models.EncryptedRecordDocument.objects.count(),
        )
        self.assertEqual(0, EncryptedStorage.delete_on_s3.call_count)
        request_from_db: (
            record_models.EncryptedRecordDocumentDeletionRequest
        ) = record_models.EncryptedRecordDocumentDeletionRequest.objects.get(
            pk=deletion_requests[2].id
        )
        self.assertEqual("de", request_from_db.state)
        self.assertEqual(
            2,
            record_models.EncryptedRecordDocumentDeletionRequest.objects.filter(
                state="re"
            ).count(),
        )
        self.assertEqual(
            1,
            record_models.EncryptedRecordDocumentDeletionRequest.objects.filter(
                state="de"
            ).count(),
        )

    def test_process_record_document_deletion_request_no_permission(self):
        deletion_requests: [
            record_models.EncryptedRecordDocumentDeletionRequest
        ] = self.add_record_document_deletion_requests_fixtures()
        self.add_process_record_document_deletion_requests_permission()

        response: Response = self.base_fixtures["users"][3]["client"].post(
            self.process_url,
            {"request_id": deletion_requests[2].id, "action": "decline"},
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            3,
            record_models.EncryptedRecordDocumentDeletionRequest.objects.filter(
                state="re"
            ).count(),
        )

    def test_process_record_document_deletion_request_wrong_id(self):
        self.add_record_document_deletion_requests_fixtures()
        self.add_process_record_document_deletion_requests_permission()

        response: Response = self.client.post(
            self.process_url, {"request_id": 123923, "action": "decline"},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__ID_NOT_FOUND["error_code"],
            response.data["error_code"],
        )
        self.assertEqual(
            3,
            record_models.EncryptedRecordDocumentDeletionRequest.objects.filter(
                state="re"
            ).count(),
        )

    def test_process_record_document_deletion_request_invalid_action(self):
        deletion_requests: [
            record_models.EncryptedRecordDocumentDeletionRequest
        ] = self.add_record_document_deletion_requests_fixtures()
        self.add_process_record_document_deletion_requests_permission()

        response: Response = self.client.post(
            self.process_url,
            {"request_id": deletion_requests[2].id, "action": "afdsadf"},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__ACTION_NOT_VALID["error_code"],
            response.data["error_code"],
        )
        self.assertEqual(
            3,
            record_models.EncryptedRecordDocumentDeletionRequest.objects.filter(
                state="re"
            ).count(),
        )

    def test_process_record_document_deletion_request_no_action(self):
        deletion_requests: [
            record_models.EncryptedRecordDocumentDeletionRequest
        ] = self.add_record_document_deletion_requests_fixtures()
        self.add_process_record_document_deletion_requests_permission()

        response: Response = self.client.post(
            self.process_url, {"request_id": deletion_requests[2].id},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__NO_ACTION_PROVIDED["error_code"],
            response.data["error_code"],
        )
        self.assertEqual(
            3,
            record_models.EncryptedRecordDocumentDeletionRequest.objects.filter(
                state="re"
            ).count(),
        )

    def test_process_record_document_deletion_request_no_id_provided(self):
        self.add_record_document_deletion_requests_fixtures()
        self.add_process_record_document_deletion_requests_permission()

        response: Response = self.client.post(
            self.process_url, {"action": "accept"},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__ID_NOT_PROVIDED["error_code"],
            response.data["error_code"],
        )
        self.assertEqual(
            3,
            record_models.EncryptedRecordDocumentDeletionRequest.objects.filter(
                state="re"
            ).count(),
        )

    def test_process_record_document_deletion_request_foreign_rlc(self):
        deletion_requests: [
            record_models.EncryptedRecordDocumentDeletionRequest
        ] = self.add_record_document_deletion_requests_fixtures()
        self.add_process_record_document_deletion_requests_permission()
        foreign_fixtures = CreateFixtures.create_foreign_rlc_fixture()

        permission: api_models.Permission = api_models.Permission.objects.get(
            name=PERMISSION_PROCESS_RECORD_DOCUMENT_DELETION_REQUESTS
        )
        has_permission: api_models.HasPermission = api_models.HasPermission(
            permission=permission,
            permission_for_rlc=foreign_fixtures["rlc"],
            user_has_permission=foreign_fixtures["users"][0]["user"],
        )
        has_permission.save()

        response: Response = foreign_fixtures["users"][0]["client"].post(
            self.process_url,
            {"request_id": deletion_requests[2].id, "action": "accept"},
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            error_codes.ERROR__API__PERMISSION__INSUFFICIENT["error_code"],
            response.data["error_code"],
        )
        self.assertEqual(
            3,
            record_models.EncryptedRecordDocumentDeletionRequest.objects.filter(
                state="re"
            ).count(),
        )


# TODO: over all check notification for accept, decline and request
