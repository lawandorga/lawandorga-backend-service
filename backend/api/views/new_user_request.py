#  law&orga - record and organization management software for refugee law clinics
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
from backend.api.models.notification import Notification
from backend.static.permissions import PERMISSION_ACCEPT_NEW_USERS_RLC
from backend.api.serializers import (
    OldNewUserRequestSerializer,
    NewUserRequestSerializer,
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from backend.api.errors import CustomError
from backend.api.models import NewUserRequest
from backend.static import error_codes
from rest_framework import mixins
from django.utils import timezone


class NewUserRequestViewSet(
    mixins.UpdateModelMixin, mixins.ListModelMixin, GenericViewSet
):
    serializer_class = OldNewUserRequestSerializer
    queryset = NewUserRequest.objects.all()

    def list(self, request, *args, **kwargs):
        if not request.user.has_permission(
            PERMISSION_ACCEPT_NEW_USERS_RLC, for_rlc=request.user.rlc
        ):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)
        queryset = NewUserRequest.objects.filter(request_from__rlc=request.user.rlc)
        return Response(OldNewUserRequestSerializer(queryset, many=True).data)

    def update(self, request, *args, **kwargs):
        user_request = self.get_object()

        from backend.api.models import UsersRlcKeys

        if not request.user.has_permission(
            PERMISSION_ACCEPT_NEW_USERS_RLC, for_rlc=request.user.rlc
        ):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        data = {
            **request.data,
            "processed_on": timezone.now(),
            "processed": request.user,
        }
        serializer = NewUserRequestSerializer(
            instance=user_request, data=data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        new_member = user_request.request_from

        if user_request.state == "gr":

            # create the rlc encryption keys for new member
            private_key_user = request.user.get_private_key(request=request)
            aes_key_rlc = request.user.rlc.get_aes_key(
                user=request.user, private_key_user=private_key_user
            )

            new_user_rlc_keys = UsersRlcKeys(
                user=new_member, rlc=request.user.rlc, encrypted_key=aes_key_rlc,
            )
            public_key = new_member.get_public_key()
            new_user_rlc_keys.encrypt(public_key)
            new_user_rlc_keys.save()

            Notification.objects.notify_new_user_accepted(request.user, user_request)

        else:
            Notification.objects.notify_new_user_declined(request.user, user_request)

        # save the user request if everything went well
        user_request = serializer.save()

        # return response
        return Response(OldNewUserRequestSerializer(user_request).data)
