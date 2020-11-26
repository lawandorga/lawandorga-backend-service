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

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from backend.collab.views import (
    CollabDocumentConnectAPIView,
    CollabDocumentListViewSet,
    DisconnectMeetingRoomAPIView,
)

router = DefaultRouter()
router.register(
    "collab_documents", CollabDocumentListViewSet, basename="collab_documents"
)


urlpatterns = [
    url(r"", include(router.urls)),
    url(r"edit_collab_document/(?P<id>.+)/$", CollabDocumentConnectAPIView.as_view()),
    url(r"leave_editing_room/(?P<id>.+)/$", DisconnectMeetingRoomAPIView.as_view()),
]
