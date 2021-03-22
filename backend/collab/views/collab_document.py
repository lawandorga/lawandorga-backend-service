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

from typing import Any
from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request

from backend.api.errors import CustomError
from backend.api.models import Group, HasPermission, Permission
from backend.api.serializers import HasPermissionSerializer
from backend.collab.models import (
    CollabDocument,
    PermissionForCollabDocument,
)
from backend.collab.serializers import (
    CollabDocumentSerializer,
    CollabDocumentTreeSerializer,
    PermissionForCollabDocumentNestedSerializer,
    PermissionForCollabDocumentSerializer,
)
from backend.static.permissions import (
    PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC,
    PERMISSION_READ_ALL_COLLAB_DOCUMENTS_RLC,
    PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC,
)


class CollabDocumentListViewSet(viewsets.ModelViewSet):
    queryset = CollabDocument.objects.all()

    def get_queryset(self) -> QuerySet:
        if self.request.user.is_superuser:
            return self.queryset
        else:
            return self.queryset.filter(rlc=self.request.user.rlc)

    def list(self, request: Request, **kwargs: Any) -> Response:
        user_has_overall_permission: bool = (
            request.user.has_permission(
                PERMISSION_READ_ALL_COLLAB_DOCUMENTS_RLC, for_rlc=request.user.rlc
            )
            or request.user.has_permission(
                PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC, for_rlc=request.user.rlc
            )
            or request.user.has_permission(
                PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC,
                for_rlc=request.user.rlc,
            )
        )
        if user_has_overall_permission:
            queryset = self.get_queryset().exclude(path__contains="/").order_by("path")
            data = CollabDocumentTreeSerializer(
                instance=queryset,
                user=request.user,
                all_documents=self.get_queryset().order_by("path"),
                overall_permission=user_has_overall_permission,
                see_subfolders=False,
                many=True,
                context={request: request},
            ).data
        else:
            queryset = self.get_queryset().exclude(path__contains="/").order_by("path")
            data = []
            for document in queryset:
                see, direct = document.user_can_see(request.user)
                if see:
                    data.append(
                        CollabDocumentTreeSerializer(
                            instance=document,
                            user=request.user,
                            all_documents=self.get_queryset().order_by("path"),
                            overall_permission=user_has_overall_permission,
                            many=False,
                            see_subfolders=direct,
                            context={request: request},
                        ).data
                    )
        return Response(data)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        data = request.data
        # TODO: add permission check here

        created_document = CollabDocument.objects.create(
            rlc=request.user.rlc,
            path=data["path"],
            creator=request.user,
            last_editor=request.user,
        )
        return Response(CollabDocumentSerializer(created_document).data)

    @action(detail=True, methods=["get"])
    def permissions(self, request: Request, pk: int):
        try:
            document = CollabDocument.objects.get(id=pk)
        except Exception as e:
            raise CustomError("document does not exist")

        # TODO: really filter  for this? should be implicit in textdocument -> rlc
        groups = Group.objects.filter(from_rlc=request.user.rlc)
        permissions_direct = PermissionForCollabDocument.objects.filter(
            group_has_permission__in=groups, document__path=document.path
        )
        permissions_below = PermissionForCollabDocument.objects.filter(
            group_has_permission__in=groups, document__path__startswith=document.path,
        ).exclude(document__path=document.path)

        overall_permissions_strings = [
            PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC,
            PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC,
            PERMISSION_READ_ALL_COLLAB_DOCUMENTS_RLC,
        ]
        overall_permissions = Permission.objects.filter(
            name__in=overall_permissions_strings
        )
        has_permissions_for_groups = HasPermission.objects.filter(
            permission_for_rlc=request.user.rlc, permission__in=overall_permissions,
        )

        permissions_above = []
        parts = document.path.split("/")
        i = 0
        while True:
            current_path = ""
            for j in range(i + 1):
                if current_path != "":
                    current_path += "/"
                current_path += parts[j]
            as_list = list(
                PermissionForCollabDocument.objects.filter(document__path=current_path)
            )
            permissions_above += as_list
            i += 1
            if i >= parts.__len__() - 1:
                break

        # parts = document.
        return_object = {
            "from_above": PermissionForCollabDocumentNestedSerializer(
                permissions_above, many=True
            ).data,
            "from_below": PermissionForCollabDocumentNestedSerializer(
                permissions_below, many=True
            ).data,
            "direct": PermissionForCollabDocumentNestedSerializer(
                permissions_direct, many=True
            ).data,
            "general": HasPermissionSerializer(
                has_permissions_for_groups, many=True
            ).data,
        }
        return Response(return_object)
