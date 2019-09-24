#  rlcapp - record and organization management software for refugee law clinics
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
router.register('records', RecordsListViewSet, base_name='records')
router.register('origin_countries', OriginCountriesViewSet)
router.register('record_tags', RecordTagViewSet)
router.register('clients', ClientsViewSet)
router.register('record_documents', RecordDocumentViewSet)
router.register('record_document_tags', RecordDocumentTagViewSet)
router.register('record_permissions', RecordPermissionViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'statics', StaticViewSet.as_view()),
    url(r'clients_by_birthday', GetClientsFromBirthday.as_view()),
    url(r'record/(?P<id>.+)/$', RecordViewSet.as_view()),
    url(r'record/$', RecordViewSet.as_view()),
    url(r'record/(?P<id>.+)/documents$', RecordDocumentByRecordViewSet.as_view()),
    url(r'record/(?P<id>.+)/messages$', RecordMessageByRecordViewSet.as_view()),
    url(r'record/(?P<id>.+)/request_permission$', RecordPermissionRequestViewSet.as_view()),
    url(r'documents/(?P<id>.+)/$', RecordDocumentTagByDocumentViewSet.as_view()),
    url(r'record_permission_requests', RecordPermissionAdmitViewSet.as_view()),
    url(r'documents_download/(?P<id>.+)/$', RecordDocumentDownloadAllViewSet.as_view()),

]
