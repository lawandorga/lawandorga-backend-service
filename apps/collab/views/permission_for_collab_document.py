#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2021  Dominik Walser
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
from typing import Any
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from apps.api.errors import CustomError
from apps.api.models import UserProfile
from apps.collab.models import PermissionForCollabDocument
from apps.collab.serializers.permission_for_collab_document import (
    PermissionForCollabDocumentSerializer,
)
from apps.static.error_codes import ERROR__API__PERMISSION__INSUFFICIENT
from apps.static.permissions import PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC


class PermissionForCollabDocumentViewSet(viewsets.ModelViewSet):
    queryset = PermissionForCollabDocument.objects.all()
    serializer_class = PermissionForCollabDocumentSerializer

    @staticmethod
    def user_has_permission(user: UserProfile):
        if not user.has_permission(
            PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC, for_rlc=user.rlc
        ):
            raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        PermissionForCollabDocumentViewSet.user_has_permission(request.user)
        return super().create(request, *args, **kwargs)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        PermissionForCollabDocumentViewSet.user_has_permission(request.user)
        return super().destroy(request, *args, **kwargs)
