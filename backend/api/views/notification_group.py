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
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response

from backend.api.errors import CustomError
from backend.api.models import  NotificationGroup
from backend.api.serializers import NotificationGroupSerializer
from backend.static.error_codes import ERROR__API__ID_NOT_PROVIDED, ERROR__API__NOTIFICATION__UPDATE_INVALID, \
    ERROR__API__USER__NO_OWNERSHIP, ERROR__API__ID_NOT_FOUND


class NotificationGroupViewSet(viewsets.ModelViewSet):
    queryset = NotificationGroup.objects.all()
    serializer_class = NotificationGroupSerializer
