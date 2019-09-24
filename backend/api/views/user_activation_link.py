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
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.static import error_codes
from backend.api.models import UserActivationLink, NewUserRequest
from backend.api.errors import CustomError
from backend.api.serializers import UserActivationLinkSerializer


class UserActivationBackendViewSet(viewsets.ModelViewSet):
    queryset = UserActivationLink.objects.all()
    serializer_class = UserActivationLinkSerializer


class UserActivationLinkViewSet(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, id):
        try:
            user_activation = UserActivationLink.objects.get(link=id)
        except:
            raise CustomError(error_codes.ERROR__API__USER_ACTIVATION__LINK_NOT_FOUND)
        try:
            new_user_request = NewUserRequest.objects.get(request_from=user_activation.user)
        except:
            raise CustomError(error_codes.ERROR__API__NEW_USER_REQUEST__REQUEST_NOT_FOUND)

        user_activation.activated = True
        user_activation.save()

        if new_user_request.state == 'gr':
            user_activation.user.is_active = True
            user_activation.user.save()

        return Response({"success": True})


class CheckUserActivationLinkViewSet(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request, id):
        try:
            UserActivationLink.objects.get(link=id)
        except:
            raise CustomError(error_codes.ERROR__API__USER_ACTIVATION__LINK_NOT_FOUND)
        return Response({"success": True})
