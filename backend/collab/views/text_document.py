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
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from backend.api.models import UserProfile
from backend.collab.models import EditingRoom, TextDocument, TextDocumentVersion
from backend.collab.serializers import (
    EditingRoomSerializer,
    TextDocumentSerializer,
    TextDocumentVersionSerializer,
)
from backend.api.errors import CustomError
from backend.static.error_codes import ERROR__API__PERMISSION__INSUFFICIENT
from backend.static.middleware import get_private_key_from_request


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
        document = self.get_object()

        try:
            record_doc = document.get_record_document()
            # check if permission for record here
        except Exception as e:
            pass
        try:
            collab_doc = document.get_collab_document()
            if not collab_doc.user_has_permission_write(request.user):
                raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)
        except Exception as e:
            pass

        users_private_key = get_private_key_from_request(request)
        user: UserProfile = request.user
        key: str = user.get_rlcs_aes_key(users_private_key)

        data = TextDocumentSerializer(document).data
        last_version = document.get_last_published_version()
        if not last_version:
            last_version = TextDocumentVersion(
                document=document,
                content=b"",
                is_draft=False,
                creator=document.creator,
                created=document.created,
            )

        draft = document.get_draft()
        if draft:
            data["versions"] = [
                TextDocumentVersionSerializer(draft).get_decrypted_data(key),
                TextDocumentVersionSerializer(last_version).get_decrypted_data(key),
            ]
        else:
            data["versions"] = [
                TextDocumentVersionSerializer(last_version).get_decrypted_data(key),
            ]

        return Response(data)

    @action(detail=True, methods=["get", "delete"])
    def editing(self, request: Request, pk: int):
        document: TextDocument = self.get_object()

        # TODO: permission
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
