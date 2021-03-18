#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
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
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *

router = DefaultRouter()
router.register("origin_countries", OriginCountriesViewSet)
router.register("record_tags", RecordTagViewSet)
router.register("record_document_tags", RecordDocumentTagViewSet)
router.register("record_deletion_requests", EncryptedRecordDeletionRequestViewSet, basename="record_deletion_requests")
router.register("record_encryptions", RecordEncryptionViewSet)
router.register("records", EncryptedRecordViewSet, basename="e_records")
router.register("e_clients", EncryptedClientsViewSet, basename="e_clients")
router.register("pool_records", PoolRecordViewSet, basename="pool_records")
router.register("pool_consultants", PoolConsultantViewSet)
router.register("missing_record_keys", MissingRecordKeyViewSet)
router.register("record_document_deletion_requests", EncryptedRecordDocumentDeletionRequestViewSet,
                basename="record_document_deletion_requests")

urlpatterns = [
    path("", include(router.urls)),
    path("e_record/<int:id>/documents/", EncryptedRecordDocumentByRecordViewSet.as_view()),
    path("e_record/documents/<int:id>/", EncryptedRecordDocumentDownloadViewSet.as_view()),
    path("statics/", StaticViewSet.as_view()),
    path("record/<int:id>/request_permission/", EncryptedRecordPermissionRequestViewSet.as_view()),
    path("documents/<int:id>/", RecordDocumentTagByDocumentViewSet.as_view()),
    path("e_record_permission_requests/", EncryptedRecordPermissionProcessViewSet.as_view()),
    path("process_record_deletion_request/", EncryptedRecordDeletionProcessViewSet.as_view()),
    path("record_pool/", RecordPoolViewSet.as_view()),
    path("process_record_document_deletion_request/", EncryptedRecordDocumentDeletionProcessViewSet.as_view()),
]
