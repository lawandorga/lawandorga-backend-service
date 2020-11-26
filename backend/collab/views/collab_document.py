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
import logging
from django.conf import settings
from django.db.models import Q, QuerySet, Case, When, Value, IntegerField
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination

from backend.collab.models import EditingRoom, CollabDocument
from backend.collab.serializers import (
    EditingRoomSerializer,
    CollabDocumentListSerializer,
)
from backend.api.permissions import OnlyGet


class CollabDocumentListViewSet(viewsets.ModelViewSet):
    queryset = CollabDocument.objects.all()
    permission_classes = (OnlyGet,)

    def get_queryset(self) -> QuerySet:
        return self.queryset

    def list(self, request: Request, **kwargs: Any) -> Response:
        queryset = self.get_queryset()
        data = CollabDocumentListSerializer(queryset, many=True).data
        return Response(data)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        pass


class CollabDocumentConnectAPIView(APIView):
    def get(self, request: Request, id: str) -> Response:
        """
        start editing document, open new editing room if none is open, else return open room
        :param request:
        :param id:
        :return:
        """
        try:
            document = CollabDocument.objects.get(pk=id)
        except Exception as e:
            pass

        room = EditingRoom(document=document)
        room.save()
        return Response(EditingRoomSerializer(room).data)
