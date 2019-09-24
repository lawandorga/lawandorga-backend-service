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

from datetime import datetime
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
import pytz

from backend.api.errors import CustomError
from backend.api.models import NewUserRequest, UserActivationLink
from backend.api.serializers import NewUserRequestSerializer
from backend.static import error_codes
from backend.static.permissions import PERMISSION_ACCEPT_NEW_USERS_RLC


class NewUserRequestViewSet(viewsets.ModelViewSet):
    serializer_class = NewUserRequestSerializer
    queryset = NewUserRequest.objects.all()

    def list(self, request, *args, **kwargs):
        if not request.user.has_permission(PERMISSION_ACCEPT_NEW_USERS_RLC, for_rlc=request.user.rlc):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)
        queryset = NewUserRequest.objects.filter(request_from__rlc=request.user.rlc)
        return Response(NewUserRequestSerializer(queryset, many=True).data)


class NewUserRequestAdmitViewSet(APIView):
    def post(self, request):
        if not request.user.has_permission(PERMISSION_ACCEPT_NEW_USERS_RLC, for_rlc=request.user.rlc):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        if 'id' not in request.data:
            raise CustomError(error_codes.ERROR__API__NEW_USER_REQUEST__ID_NOT_PROVIDED)
        if 'action' not in request.data:
            raise CustomError(error_codes.ERROR__API__NO_ACTION_PROVIDED)

        try:
            new_user_request = NewUserRequest.objects.get(pk=request.data['id'])
        except:
            raise CustomError(error_codes.ERROR__API__ID_NOT_FOUND)
        try:
            user_activation_link = UserActivationLink.objects.get(user=new_user_request.request_from)
        except:
            raise CustomError(error_codes.ERROR__API__NEW_USER_REQUEST__NO_USER_ACTIVATION_LINK)

        action = request.data['action']
        if action != 'accept' and action != 'decline':
            raise CustomError(error_codes.ERROR__API__ACTION_NOT_VALID)

        new_user_request.request_processed = request.user
        new_user_request.processed_on = datetime.utcnow().replace(tzinfo=pytz.utc)
        if action == 'accept':
            new_user_request.state = 'gr'
            if user_activation_link.activated:
                new_user_request.request_from.is_active = True
                new_user_request.request_from.save()
        else:
            new_user_request.state = 'de'
        new_user_request.save()
        return Response(NewUserRequestSerializer(new_user_request).data)
