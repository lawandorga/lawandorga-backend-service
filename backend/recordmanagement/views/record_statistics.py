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
from datetime import date
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
            out_tags.append(
                {
                    "name": tag.name,
                    "value": tag.e_tagged.filter(from_rlc=request.user.rlc).count(),
                }
            )

        rlc_records: [models.EncryptedRecord] = models.EncryptedRecord.objects.filter(
            from_rlc=request.user.rlc
        )
        total_records = rlc_records.count()
        total_records_open = rlc_records.filter(state="op").count()
        total_records_waiting = rlc_records.filter(state="wa").count()
        total_records_closed = rlc_records.filter(state="cl").count()
        total_records_working = rlc_records.filter(state="wo").count()

        # first_record: models.EncryptedRecord = (from_rlc=request.user.rlc
        #     models.EncryptedRecord.objects.filter(from_rlc=request.user.rlc)
        #     .order_by("created_on")
        #     .first()
        # )
        # timedelta = date.today() - first_record.created_on

        return Response(
            {
                "tags": out_tags,
                "records": {
                    "total": {
                        "overall": total_records,
                        "open": total_records_open,
                        "waiting": total_records_waiting,
                        "closed": total_records_closed,
                        "working": total_records_working,
                    }
                },
            }
        )
