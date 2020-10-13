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


from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
# recheck all
router.register("records", RecordsListViewSet, basename="record")
router.register("origin_countries", OriginCountriesViewSet)
router.register("record_tags", RecordTagViewSet)
router.register("clients", ClientsViewSet)
router.register("record_documents", RecordDocumentViewSet)
router.register("record_document_tags", RecordDocumentTagViewSet)
router.register("record_permissions", RecordPermissionViewSet)
router.register(
    "record_deletion_requests",
    EncryptedRecordDeletionRequestViewSet,
    basename="record_deletion_requests",
)
# router.register('record_deletion_requests', RecordDeletionRequestViewSet) OLD
# encryption
router.register("record_encryptions", RecordEncryptionViewSet)
router.register("e_records", EncryptedRecordsListViewSet, basename="e_records")
router.register(
    "e_clients", EncryptedClientsViewSet, basename="e_records"
)  # TODO: add all encrypted fields here
router.register("pool_records", PoolRecordViewSet, basename="pool_records")
router.register("pool_consultants", PoolConsultantViewSet)
router.register("missing_record_keys", MissingRecordKeyViewSet)
router.register(
    "record_document_deletion_requests",
    EncryptedRecordDocumentDeletionRequestViewSet,
    basename="record_document_deletion_requests",
)


urlpatterns = [
    url(r"", include(router.urls)),
    url(
        r"e_record/(?P<id>.+)/documents/$",
        EncryptedRecordDocumentByRecordViewSet.as_view(),
    ),
    url(
        r"e_record/documents/(?P<id>.+)/$",
        EncryptedRecordDocumentDownloadViewSet.as_view(),
    ),
    url(r"statics", StaticViewSet.as_view()),
    url(r"e_clients_by_birthday", GetEncryptedClientsFromBirthday.as_view()),
    url(r"clients_by_birthday", GetClientsFromBirthday.as_view()),  # deprecated
    url(r"e_record/(?P<id>.+)/$", EncryptedRecordViewSet.as_view()),
    url(r"e_record/$", EncryptedRecordViewSet.as_view()),
    url(
        r"record/(?P<id>.+)/documents$", RecordDocumentByRecordViewSet.as_view()
    ),  # deprecated
    url(
        r"e_record/(?P<id>.+)/messages$",
        EncryptedRecordMessageByRecordViewSet.as_view(),
    ),
    # url(r'record/(?P<id>.+)/messages$', RecordMessageByRecordViewSet.as_view()),            # deprecated
    url(
        r"record/(?P<id>.+)/request_permission$",
        EncryptedRecordPermissionRequestViewSet.as_view(),
    ),
    # url(r'record/(?P<id>.+)/request_permission$', RecordPermissionRequestViewSet.as_view()), OLD
    url(r"documents/(?P<id>.+)/$", RecordDocumentTagByDocumentViewSet.as_view()),
    url(
        r"e_record_permission_requests",
        EncryptedRecordPermissionProcessViewSet.as_view(),
    ),
    url(
        r"record_permission_requests", RecordPermissionAdmitViewSet.as_view()
    ),  # deprecated
    url(
        r"documents_download/(?P<id>.+)/$", RecordDocumentDownloadAllViewSet.as_view()
    ),  # deprecated
    url(
        r"process_record_deletion_request",
        EncryptedRecordDeletionProcessViewSet.as_view(),
    ),
    # url(r'process_record_deletion_request', RecordDeletionProcessViewSet.as_view()),    # OLD
    # url(r'^e_upload/$', EncryptedRecordDocumentsUploadViewSet.as_view()),               # deprecated
    url(
        r"^upload/(?P<filename>[^/]+)$", RecordDocumentUploadEncryptViewSet.as_view()
    ),  # deprecated
    url(r"record_pool/$", RecordPoolViewSet.as_view()),
    url(
        r"process_record_document_deletion_request/$",
        EncryptedRecordDocumentDeletionProcessViewSet.as_view(),
    ),
]
