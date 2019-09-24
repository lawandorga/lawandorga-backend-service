#  rlcapp - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
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
from datetime import datetime
import pytz

from backend.recordmanagement import models, serializers
from backend.static import error_codes
from backend.api.errors import CustomError
from backend.static import permissions


class RecordPermissionViewSet(viewsets.ModelViewSet):
    queryset = models.RecordPermission.objects.all()
    serializer_class = serializers.RecordPermissionSerializer


class RecordPermissionRequestViewSet(APIView):
    def post(self, request, id):
        if not request.user.has_permission(permissions.PERMISSION_VIEW_RECORDS_RLC, for_rlc=request.user.rlc):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)
        try:
            record = models.Record.objects.get(pk=id)
        except Exception as e:
            raise CustomError(error_codes.ERROR__RECORD__RECORD__NOT_EXISTING)
        if record.user_has_permission(request.user):
            raise CustomError(error_codes.ERROR__RECORD__PERMISSION__ALREADY_WORKING_ON)

        if models.RecordPermission.objects.filter(record=record, request_from=request.user, state='re').count() >= 1:
            raise CustomError(error_codes.ERROR__RECORD__PERMISSION__ALREADY_REQUESTED)
        can_edit = False
        if 'can_edit' in request.data:
            can_edit = request.data['can_edit']

        permission = models.RecordPermission(request_from=request.user, record=record, can_edit=can_edit)
        permission.save()
        return Response(serializers.RecordPermissionSerializer(permission).data)


class RecordPermissionAdmitViewSet(APIView):
    def get(self, request):
        """
        used from admins to see which permission requests are for the own rlc in the system
        :param request:
        :return:
        """
        user = request.user
        if not user.has_permission(permissions.PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC, for_rlc=user.rlc):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)
        requests = models.RecordPermission.objects.filter(record__from_rlc=user.rlc)
        # if requests.count() == 0:
        #     raise CustomError(error_codes)
        return Response(serializers.RecordPermissionSerializer(requests, many=True).data)

    def post(self, request):
        """
        used to admit or decline a given permission request
        :param request:
        :return:
        """
        user = request.user
        if not user.has_permission(permissions.PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC, for_rlc=user.rlc):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)
        if 'id' not in request.data:
            raise CustomError(error_codes.ERROR__RECORD__PERMISSION__ID_NOT_PROVIDED)
        try:
            permission_request = models.RecordPermission.objects.get(pk=request.data['id'])
        except Exception as e:
            raise CustomError(error_codes.ERROR__RECORD__PERMISSION__ID_NOT_FOUND)

        if 'action' not in request.data:
            raise CustomError(error_codes.ERROR__API__NO_ACTION_PROVIDED)
        action = request.data['action']
        if action != 'accept' and action != 'decline':
            raise CustomError(error_codes.ERROR__RECORD__PERMISSION__NO_VALID_ACTION_PROVIDED)

        permission_request.request_processed = user
        permission_request.processed_on = datetime.utcnow().replace(tzinfo=pytz.utc)
        if action == 'accept':
            permission_request.state = 'gr'
        else:
            permission_request.state = 'de'
        permission_request.save()
        return Response(serializers.RecordPermissionSerializer(permission_request).data)

