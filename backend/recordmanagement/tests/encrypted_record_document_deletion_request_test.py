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

        # permission: api_models.Permission = api_models.Permission.objects.get(
        #     name=PERMISSION_VIEW_RECORDS_RLC
        # )
        # has_permission: api_models.HasPermission = api_models.HasPermission(
        #     permission=permission,
        #     permission_for_rlc=self.base_fixtures["rlc"],
        #     group_has_permission=self.base_fixtures["groups"][0],
        # )
        # has_permission.save()
        # has_permission: api_models.HasPermission = api_models.HasPermission(
        #     permission=permission,
        #     permission_for_rlc=self.base_fixtures["rlc"],
        #     group_has_permission=self.base_fixtures["groups"][1],
        # )
        # has_permission.save()

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


# TODO
# request deletion
# foreign rlc
# no permission for record
# wrong id
# doubled same
# doubled other

# view deletion request list
# no permission
# unauthenticated
# foreign rlc

# process deletion request
# accept (check if delete on s3 called))
# accept multiple (all get accepted)
# decline
# decline (multiple, just one gets declined)
# no permission
# wrong id
# wrong method
# no method
# no id?
# foreign rlc
# unauthenticated

# TODO: over all check notification for accept, decline and request
