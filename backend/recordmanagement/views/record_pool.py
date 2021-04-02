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

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from backend.api.errors import CustomError
from backend.recordmanagement.models.pool_consultant import PoolConsultant
from backend.recordmanagement.models.pool_record import PoolRecord
from backend.recordmanagement.serializers import (
    PoolConsultantSerializer,
    PoolRecordSerializer,
)
from backend.static import error_codes
from backend.static.permissions import PERMISSION_CAN_CONSULT


class RecordPoolViewSet(APIView):
    def get(self, request):
        user = request.user
        if not user.has_permission(PERMISSION_CAN_CONSULT, for_rlc=user.rlc):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        queryset = PoolRecord.objects.filter(record__from_rlc=user.rlc)
        if queryset.count() > 0:
            data = PoolRecordSerializer(queryset, many=True).data
            return_val = {"type": "records"}
            return_val.update({"entries": data})
            return Response(return_val)

        queryset = PoolConsultant.objects.filter(consultant__rlc=user.rlc)
        if queryset.count() > 0:
            data = PoolConsultantSerializer(queryset, many=True).data
            return_val = {"type": "consultants"}
            return_val.update({"entries": data})
            number_of_own_enlistings = PoolConsultant.objects.filter(
                consultant=user
            ).count()
            return_val.update({"number_of_own_enlistings": number_of_own_enlistings})
            return Response(return_val)

        return Response({"type": "empty"})
