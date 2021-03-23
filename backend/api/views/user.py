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
from django.contrib.auth import authenticate
from rest_framework.authtoken.serializers import AuthTokenSerializer
from backend.api.models.notification import Notification
from rest_framework.authtoken.models import Token
from backend.api.models.permission import Permission
from rest_framework.permissions import IsAuthenticated
from backend.static.error_codes import *
from backend.static.middleware import get_private_key_from_request
from backend.static.encryption import RSAEncryption
from backend.api.models import NewUserRequest, UserActivationLink
from backend.static.date_utils import parse_date
from rest_framework.decorators import action
from backend.api.serializers import OldUserSerializer, UserCreateSerializer, UserProfileNameSerializer, \
    RlcSerializer, UserProfileForeignSerializer, UserSerializer, UserUpdateSerializer
from rest_framework.response import Response
from rest_framework.request import Request
from backend.static.emails import EmailSender, FrontendLinks
from django.forms.models import model_to_dict
from backend.api.models import UserProfile, Rlc, UserEncryptionKeys, NotificationGroup
from backend.api.errors import CustomError
from rest_framework import viewsets, filters, status
from backend.static import permissions
from django.http import QueryDict
from datetime import datetime
import pytz


class SpecialPermission(IsAuthenticated):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return super().has_permission(request, view)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = UserProfile.objects.none()
    filter_backends = (filters.SearchFilter,)
    permission_classes = [SpecialPermission]
    search_fields = (
        "name",
        "email",
    )

    def get_authenticators(self):
        if self.request.method == 'POST':
            return []
        return super().get_authenticators()

    def get_serializer_class(self):
        if self.request.method in ['POST']:
            return UserCreateSerializer
        elif self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.request.method == 'POST':
            return super().get_queryset()
        return UserProfile.objects.filter(rlc=self.request.user.rlc)

    def create(self, request, *args, **kwargs):
        # create the user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # new user request
        user_request = NewUserRequest.objects.create(request_from=user)

        # new user activation link
        activation_link = UserActivationLink.objects.create(user=user)
        EmailSender.send_user_activation_email(
            user, FrontendLinks.get_user_activation_link(activation_link)
        )

        # notify about the new user
        Notification.objects.notify_new_user_request(user, user_request)

        # return the success response
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        if request.user.is_superuser:
            queryset = UserProfile.objects.all()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            queryset = UserProfile.objects.filter(rlc=request.user.rlc, is_active=True)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = UserProfileNameSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = UserProfileNameSerializer(queryset, many=True)
            return Response(serializer.data)

    def retrieve(self, request, pk=None, **kwargs):
        if pk is None:
            raise CustomError(ERROR__API__USER__ID_NOT_PROVIDED)
        try:
            user = UserProfile.objects.get(pk=pk)
        except Exception as e:
            raise CustomError(ERROR__API__USER__NOT_FOUND)

        if request.user.rlc != user.rlc:
            if request.user.is_superuser or request.user.has_permission(
                permissions.PERMISSION_VIEW_FULL_USER_DETAIL_OVERALL
            ):
                serializer = OldUserSerializer(user)
            else:
                raise CustomError(ERROR__API__USER__NOT_SAME_RLC)
        else:
            if request.user.has_permission(
                permissions.PERMISSION_VIEW_FULL_USER_DETAIL_RLC
            ):
                serializer = OldUserSerializer(user)
            else:
                serializer = UserProfileForeignSerializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def logout(self, request: Request):
        if not request.user.is_authenticated:
            return Response()
        Token.objects.filter(user=request.user).delete()
        return Response()

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['get', 'post'])
    def inactive(self, request: Request):
        if request.method == 'GET':
            if not request.user.has_permission(permissions.PERMISSION_ACTIVATE_INACTIVE_USERS_RLC,
                                               for_rlc=request.user.rlc):
                raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)

            inactive_users = UserProfile.objects.filter(rlc=request.user.rlc, is_active=False)
            return Response(UserSerializer(inactive_users, many=True).data)

        elif request.method == 'POST':
            if not request.user.has_permission(
                permissions.PERMISSION_ACTIVATE_INACTIVE_USERS_RLC, for_rlc=request.user.rlc
            ):
                raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)
            # method and user_id
            if request.data["method"] == "activate":
                try:
                    user = UserProfile.objects.get(pk=request.data["user_id"])
                except:
                    raise CustomError(ERROR__API__USER__NOT_FOUND)

                granting_users_private_key = get_private_key_from_request(request)
                rlcs_aes_key = request.user.get_rlcs_aes_key(granting_users_private_key)
                user.generate_rlc_keys_for_this_user(rlcs_aes_key)

                user.is_active = True
                user.save()
                return Response(OldUserSerializer(user).data)
            raise CustomError(ERROR__API__ACTION_NOT_VALID)

        return Response({})


class LoginViewSet(viewsets.ViewSet):
    """checks email and password and returns auth token"""

    serializer_class = AuthTokenSerializer
    authentication_classes = ()
    permission_classes = ()

    def create(self, request):
        """
        use the obtainauthToken APIView to validate and create a token
        additionally add all important information for app usage
        like static possible states, possible permissions and so on
        Args:
            request: the request with data: 'username' and 'password"

        Returns:
        token, information and permissions of user
        private_key of user
        all possible permissions, country states, countries, clients, record states, consultants
        """
        user_password = request.data["password"]
        data = {"password": user_password, "username": request.data["username"].lower()}
        serializer = self.serializer_class(data=data)
        LoginViewSet.check_if_user_active(data["username"])
        if serializer.is_valid():
            token, created = Token.objects.get_or_create(
                user=serializer.validated_data["user"]
            )
            Token.objects.filter(user=token.user).exclude(
                key=token.key
            ).delete()  # delete old tokens, keep new
            if not created:
                # update the created time of the token to keep it valid
                token.created = datetime.utcnow().replace(tzinfo=pytz.utc)
                token.save()
            # get encryption keys
            encryption_keys = UserEncryptionKeys.objects.get(user=token.user)
            if not encryption_keys:
                private, public = RSAEncryption.generate_keys()
                encryption_keys = UserEncryptionKeys(
                    user=token.user, private_key=private, public_key=public
                )
                encryption_keys.save()
            # decrypt keys with users password (or: if not encrypted atm, encrypt them with users password)
            private_key = encryption_keys.decrypt_private_key(user_password)

            # from backend.recordmanagement.helpers import (
            #     resolve_missing_record_key_entries,
            # )

            # resolve_missing_record_key_entries(token.user, private_key)
            # TODO: superuser?
            if not token.user.is_superuser:
                from backend.api.helpers import resolve_missing_rlc_keys_entries

                resolve_missing_rlc_keys_entries(token.user, private_key)

            return Response(LoginViewSet.get_login_data(token.key, private_key))
        raise CustomError(ERROR__API__LOGIN__INVALID_CREDENTIALS)

    def get(self, request):
        token = request.META["HTTP_AUTHORIZATION"].split(" ")[1]
        try:
            Token.objects.get(key=token)
        except:
            raise CustomError(ERROR__API__NOT_AUTHENTICATED)

        return Response(LoginViewSet.get_login_data(token))

    @staticmethod
    def get_login_data(token, private_key=None):
        user = Token.objects.get(key=token).user
        serialized_user = OldUserSerializer(user).data
        serialized_rlc = RlcSerializer(user.rlc).data

        notifications = NotificationGroup.objects.filter(user=user, read=False).count()

        statics = LoginViewSet.get_statics(user)
        return_object = {
            "token": token,
            "user": serialized_user,
            "rlc": serialized_rlc,
            "notifications": notifications,
        }
        return_object.update(statics)
        if private_key:
            return_object.update({"users_private_key": private_key})

        return return_object

    @staticmethod
    def get_statics(user):
        user_permissions = [
            model_to_dict(perm) for perm in user.get_all_user_permissions()
        ]
        overall_permissions = [
            model_to_dict(permission) for permission in Permission.objects.all()
        ]
        user_states_possible = UserProfile.user_states_possible
        user_record_states_possible = UserProfile.user_record_states_possible

        return {
            "permissions": user_permissions,
            "all_permissions": overall_permissions,
            "user_states": user_states_possible,
            "user_record_states": user_record_states_possible,
        }

    @staticmethod
    def check_if_user_active(user_email):
        """
        checks if user exists and if user is active
        :param user_email: string, email of user
        :return:
        """
        try:
            user = UserProfile.objects.get(email=user_email)
        except:
            raise CustomError(ERROR__API__USER__NOT_FOUND)
        if not user.is_active:
            raise CustomError(ERROR__API__USER__INACTIVE)
