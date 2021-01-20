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
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from backend.api.models import UserProfile
from backend.collab.models import EditingRoom, TextDocument, TextDocumentVersion
from backend.collab.serializers import (
    EditingRoomSerializer,
    TextDocumentSerializer,
    TextDocumentVersionSerializer,
    TextDocumentVersionListSerializer,
)
from backend.api.errors import CustomError
from backend.static.error_codes import (
    ERROR__API__ID_NOT_FOUND,
    ERROR__API__PARAMS_NOT_VALID,
)
from backend.static.middleware import get_private_key_from_request


class TextDocumentVersionModelViewSet(viewsets.ModelViewSet):
    queryset = TextDocumentVersion.objects.all()

    def get_queryset(self) -> QuerySet:
        if self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(document_rlc=self.request.user.rlc)

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        pass

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        pass

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            version = TextDocumentVersion.objects.get(pk=kwargs["pk"])
        except Exception as e:
            raise CustomError(ERROR__API__ID_NOT_FOUND)

        users_private_key = get_private_key_from_request(request)
        key: str = request.user.get_rlcs_aes_key(users_private_key)

        return Response(TextDocumentVersionSerializer(version).get_decrypted_data(key))


class VersionsOfTextDocumentViewSet(APIView):
    def get(self, request: Request, id: str) -> Response:
        try:
            document = TextDocument.objects.get(pk=id)
        except Exception as e:
            raise CustomError(ERROR__API__ID_NOT_FOUND)

        users_private_key = get_private_key_from_request(request)
        key: str = request.user.get_rlcs_aes_key(users_private_key)

        versions = document.versions.all().order_by("-created")

        full_data = [
            TextDocumentVersionSerializer(versions.first()).get_decrypted_data(key),
            *TextDocumentVersionListSerializer(versions, many=True).data[1:],
        ]
        return Response(full_data)

    def post(self, request: Request, id: str) -> Response:
        try:
            document: TextDocument = TextDocument.objects.get(pk=id)
        except Exception as e:
            raise CustomError(ERROR__API__ID_NOT_FOUND)

        if "content" not in request.data or "is_draft" not in request.data:
            raise CustomError(ERROR__API__PARAMS_NOT_VALID)

        TextDocumentVersion.objects.filter(document=document, is_draft=True).delete()

        users_private_key = get_private_key_from_request(request)
        user: UserProfile = request.user
        key: str = user.get_rlcs_aes_key(users_private_key)

        last_version: TextDocumentVersion = document.get_last_published_version()
        if last_version:
            last_content = TextDocumentVersionSerializer(
                last_version
            ).get_decrypted_data(key)["content"]
            if request.data["content"] == last_content:
                return Response(
                    TextDocumentVersionSerializer(last_version).get_decrypted_data(key),
                    status=201,
                )

        version = TextDocumentVersion.create(
            request.data["content"], request.data["is_draft"], key, user, document
        )

        return Response(
            TextDocumentVersionSerializer(version).get_decrypted_data(key), status=201
        )
