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
from apps.recordmanagement.views import *
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register("origin_countries", OriginCountryViewSet)
router.register("record_document_tags", RecordDocumentTagViewSet)
router.register("record_deletion_requests", EncryptedRecordDeletionRequestViewSet)
router.register("record_encryptions", RecordEncryptionViewSet)
router.register("records", EncryptedRecordViewSet)
router.register("e_clients", EncryptedClientViewSet)
router.register("pool_records", PoolRecordViewSet)
router.register("pool_consultants", PoolConsultantViewSet)
router.register("consultants", ConsultantViewSet)
router.register('record_documents', EncryptedRecordDocumentViewSet)
router.register('record_permission_requests', EncryptedRecordPermissionProcessViewSet)
router.register('tags', TagViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "process_record_deletion_request/",
        EncryptedRecordDeletionProcessViewSet.as_view(),
    ),
    path("record_pool/", RecordPoolViewSet.as_view()),
    path("statistics/", RecordStatisticsViewSet.as_view(), ),
]
