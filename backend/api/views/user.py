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
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken

from backend.api.models.notification import Notification
from rest_framework.authtoken.models import Token
from backend.api.models.permission import Permission
from rest_framework.permissions import IsAuthenticated
from backend.static.error_codes import *
from backend.static.middleware import get_private_key_from_request
from backend.static.encryption import RSAEncryption
from rest_framework.decorators import action
from backend.api.serializers import OldUserSerializer, UserCreateSerializer, UserProfileNameSerializer, \
    RlcSerializer, UserProfileForeignSerializer, UserSerializer, UserUpdateSerializer
from rest_framework.response import Response
from rest_framework.request import Request
from django.forms.models import model_to_dict
from backend.api.models import NewUserRequest, UserProfile, UserEncryptionKeys, NotificationGroup, \
    account_activation_token
from backend.api.errors import CustomError
from rest_framework import viewsets, filters, status
from backend.static import permissions
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
    filter_backends = [filters.SearchFilter]
    permission_classes = [SpecialPermission]
    search_fields = ["name", "email"]

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
        if self.request.user.is_authenticated:
            return UserProfile.objects.filter(rlc=self.request.user.rlc)
        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        # create the user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # new user request
        user_request = NewUserRequest.objects.create(request_from=user)

        # send the user activation link email
        token = account_activation_token.make_token(user)
        link = '{}activate-account/{}/{}/'.format(settings.FRONTEND_URL, user.id, token)
        subject = "Law & Orga Registration"
        message = "Law & Orga - Activate your account here: {}".format(link)
        html_message = loader.render_to_string("email_templates/activate_account.html", {"url": link})
        send_mail(
            subject=subject,
            html_message=html_message,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
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

    @action(detail=False, methods=['post'], permission_classes=[], authentication_classes=[])
    def login(self, request: Request):
        serializer = AuthTokenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user: UserProfile = serializer.validated_data['user']
        password = serializer.validated_data['password']

        # check if user active and user accepted in rlc
        if not user.email_confirmed:
            message = 'You can not login, yet. Please confirm your email first.'
            return Response({'non_field_errors': [message]}, status.HTTP_400_BAD_REQUEST)
        if hasattr(user, 'accepted') and not user.accepted.state == 'gr':
            message = 'You can not login, yet. Your RLC needs to accept you as their member.'
            return Response({'non_field_errors': [message]}, status.HTTP_400_BAD_REQUEST)

        # create the token and set the time if not created to keep it valid
        token, created = Token.objects.get_or_create(user=user)
        if not created:
            token.created = timezone.now()
            token.save()

        # get the user's private key
        private_key = user.get_private_key(password)

        # build the response
        data = {
            "token": token.key,
            "email": user.email,
            "id": user.pk,
            "users_private_key": private_key
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='statics/(?P<token>[^/.]+)')
    def statics(self, request: Request, token=None, *args, **kwargs):
        token = Token.objects.get(key=token)
        user = token.user

        notifications = NotificationGroup.objects.filter(user=user, read=False).count()
        user_permissions = [model_to_dict(perm) for perm in user.get_all_user_permissions()]
        overall_permissions = [model_to_dict(permission) for permission in Permission.objects.all()]
        user_states_possible = UserProfile.user_states_possible
        user_record_states_possible = UserProfile.user_record_states_possible

        data = {
            "user": OldUserSerializer(user).data,
            "rlc": RlcSerializer(user.rlc).data,
            "notifications": notifications,
            "permissions": user_permissions,
            "all_permissions": overall_permissions,
            "user_states": user_states_possible,
            "user_record_states": user_record_states_possible,
        }

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def logout(self, request: Request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response()
        Token.objects.filter(user=request.user).delete()
        return Response()

    @action(detail=True, methods=['get'], url_path='activate/(?P<token>[^/.]+)', permission_classes=[],
            authentication_classes=[])
    def activate(self, request, token, *args, **kwargs):
        self.queryset = UserProfile.objects.all()
        user = self.get_object()

        if account_activation_token.check_token(user, token):
            user.email_confirmed = True
            user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            data = {
                'message': 'The confirmation link is invalid, possibly because it has already been used.'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

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
