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
from backend.collab.serializers import EditingRoomSerializer


class DisconnectMeetingRoomAPIView(APIView):
    def post(self, request: Request, id: str):
        """
        editing room closed from user, send content of current doc to save it
        :param request:
        :param id:
        :return:
        """
        pass
