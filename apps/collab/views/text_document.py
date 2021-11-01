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
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet
from apps.api.models import UserProfile
from apps.collab.models import EditingRoom, TextDocument, TextDocumentVersion
from apps.collab.serializers import (
    EditingRoomSerializer,
    TextDocumentSerializer,
    TextDocumentVersionDetailSerializer,
    TextDocumentVersionListSerializer,
    TextDocumentVersionSerializer,
    UserProfileNameSerializer,
)
from apps.api.errors import CustomError
from apps.static.error_codes import ERROR__API__PERMISSION__INSUFFICIENT
from apps.static.middleware import get_private_key_from_request


class TextDocumentModelViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = TextDocument.objects.all()

    def get_queryset(self) -> QuerySet:
        if self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(rlc=self.request.user.rlc)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        document: TextDocument = self.get_object()

        users_private_key = get_private_key_from_request(request)
        user: UserProfile = request.user
        key: str = user.get_rlc_aes_key(users_private_key)

        data = TextDocumentSerializer(document).data
        last_version: TextDocumentVersion = document.get_last_published_version()
        if not last_version:
            last_version = TextDocumentVersion(
                document=document,
                content=b"",
                is_draft=False,
                creator=document.creator,
                created=document.created,
            )

        data.update(
            {
                "last_editor": UserProfileNameSerializer(last_version.creator).data,
                "last_edited": last_version.created,
                "read": document.user_has_permission_read(request.user),
                "write": document.user_has_permission_write(request.user),
            }
        )
        draft: TextDocumentVersion = document.get_draft()

        last_version.decrypt(key)
        if draft:
            draft.decrypt(key)
            data["versions"] = [
                TextDocumentVersionSerializer(draft).data,
                TextDocumentVersionSerializer(last_version).data,
            ]
        else:
            data["versions"] = [
                TextDocumentVersionSerializer(last_version).data,
            ]
        return Response(data)

    @action(detail=True, methods=["get", "delete"])
    def editing(self, request: Request, pk: int):
        document: TextDocument = self.get_object()

        if not document.user_has_permission_write(request.user):
            raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)

        if request.method == "GET":
            existing = EditingRoom.objects.filter(document=document).first()
            did_create = False
            if existing:
                room = existing
            else:
                room = EditingRoom(document=document)
                room.save()
                did_create = True
            response_obj = EditingRoomSerializer(room).data
            response_obj.update({"did_create": did_create})
            return Response(response_obj)
        if request.method == "DELETE":
            EditingRoom.objects.filter(document=document).delete()
            return Response({"success": True})

    @action(methods=["get", "post"], detail=True)
    def versions(self, request: Request, *args, **kwargs):
        document: TextDocument = self.get_object()
        user: UserProfile = request.user
        users_private_key = get_private_key_from_request(request)
        key: str = user.get_rlc_aes_key(users_private_key)

        if request.method == "GET":
            versions = document.versions.all().order_by("-created")

            first: TextDocumentVersion = versions.first()
            first.decrypt(key)
            full_data = [
                TextDocumentVersionDetailSerializer(first).data,
                *TextDocumentVersionListSerializer(versions, many=True).data[1:],
            ]
            return Response(full_data)
        if request.method == "POST":
            if not document.user_has_permission_write(request.user):
                raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)

            request.data["creator"] = user.pk
            request.data["document"] = document.pk

            serializer = TextDocumentVersionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            TextDocumentVersion.objects.filter(
                document=document, is_draft=True
            ).delete()

            last_version: TextDocumentVersion = document.get_last_published_version()
            if last_version:
                last_version.decrypt(key)
                if request.data["content"] == last_version.content:
                    return Response(
                        TextDocumentVersionDetailSerializer(last_version).data,
                        status=status.HTTP_201_CREATED,
                    )

            version = TextDocumentVersion(**serializer.validated_data)
            version.encrypt(key)
            version.save()

            version.decrypt(key)
            return Response(
                TextDocumentVersionSerializer(version).data,
                status=status.HTTP_201_CREATED,
            )
