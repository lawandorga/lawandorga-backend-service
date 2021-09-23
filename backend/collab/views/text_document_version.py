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
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from backend.api.models import UserProfile
from backend.collab.models import TextDocument, TextDocumentVersion
from backend.collab.serializers import (
    TextDocumentVersionDetailSerializer,
    TextDocumentVersionSerializer,
    TextDocumentVersionListSerializer,
)
from backend.api.errors import CustomError
from backend.static.error_codes import (
    ERROR__API__ID_NOT_FOUND,
    ERROR__API__PARAMS_NOT_VALID,
    ERROR__API__PERMISSION__INSUFFICIENT,
)

from backend.static.middleware import get_private_key_from_request


class TextDocumentVersionModelViewSet(viewsets.ModelViewSet):
    queryset = TextDocumentVersion.objects.all()

    def get_queryset(self) -> QuerySet:
        return self.queryset.filter(document__rlc=self.request.user.rlc)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        version: TextDocumentVersion = self.get_object()

        users_private_key = get_private_key_from_request(request)
        rlcs_aes_key = request.user.get_rlc_aes_key(users_private_key)

        version.decrypt(rlcs_aes_key)
        return Response(TextDocumentVersionDetailSerializer(version).data)
