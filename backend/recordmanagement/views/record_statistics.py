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
import logging
from django.conf import settings
from django.db.models import Q, QuerySet, Case, When, Value, IntegerField
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination

from backend.api.errors import CustomError
from backend.api.models import Notification, UserEncryptionKeys, UserProfile
from backend.recordmanagement import models, serializers
from backend.static import error_codes, permissions
from backend.static.emails import EmailSender
from backend.static.encryption import AESEncryption, RSAEncryption
from backend.static.frontend_links import FrontendLinks
from backend.static.middleware import get_private_key_from_request
from backend.api.permissions import OnlyGet


class RecordStatisticsViewSet(APIView):
    def get(self, request: Request):
        record_tags = models.RecordTag.objects.all()
        out_tags = []
        for tag in record_tags:
            out_tags.append({"name": tag.name, "value": tag.e_tagged.count()})
        return Response(out_tags)
