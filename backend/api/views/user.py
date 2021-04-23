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
from rest_framework.authtoken.serializers import AuthTokenSerializer
from backend.api.models.notification import Notification
from rest_framework.authtoken.models import Token
from backend.api.models.permission import Permission
from backend.static.permissions import (
    PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC,
    PERMISSION_MANAGE_USERS,
)
from rest_framework.permissions import IsAuthenticated
from backend.static.error_codes import *
from backend.static.middleware import get_private_key_from_request
from rest_framework.decorators import action
from backend.api.serializers import (
    OldUserSerializer,
    UserCreateSerializer,
    UserProfileNameSerializer,
    RlcSerializer,
    UserProfileForeignSerializer,
    UserSerializer,
    UserUpdateSerializer,
    UserPasswordResetSerializer,
    UserPasswordResetConfirmSerializer,
)
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.request import Request
from django.forms.models import model_to_dict
from backend.api.models import (
    NewUserRequest,
    UserProfile,
    NotificationGroup,
    PasswordResetTokenGenerator,
    AccountActivationTokenGenerator,
)
from backend.api.errors import CustomError
from django.core.mail import send_mail
from django.template import loader
from rest_framework import viewsets, filters, status
from backend.static import permissions
from django.utils import timezone
from django.conf import settings


class SpecialPermission(IsAuthenticated):
    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        return super().has_permission(request, view)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = UserProfile.objects.none()
    filter_backends = [filters.SearchFilter]
    permission_classes = [SpecialPermission]
    search_fields = ["name", "email"]

    def get_authenticators(self):
        # self.action == 'create' would be better here but self.action is not set yet
        if self.request.path == "/api/profiles/" and self.request.method == "POST":
            return []
        return super().get_authenticators()

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.action == "activate" or self.action == 'password_reset_confirm':
            return UserProfile.objects.all().select_related("accepted")
        else:
            return UserProfile.objects.filter(rlc=self.request.user.rlc).select_related(
                "accepted"
            )

    def create(self, request, *args, **kwargs):
        # create the user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # new user request
        user_request = NewUserRequest.objects.create(request_from=user)

        # send the user activation link email
        token = AccountActivationTokenGenerator().make_token(user)
        link = "{}activate-account/{}/{}/".format(settings.FRONTEND_URL, user.id, token)
        subject = "Law & Orga Registration"
        message = "Law & Orga - Activate your account here: {}".format(link)
        html_message = loader.render_to_string(
            "email_templates/activate_account.html", {"url": link}
        )
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
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def retrieve(self, request, pk=None, **kwargs):
        user = self.get_object()
        serializer = UserProfileForeignSerializer(user)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        if not request.user.has_permission(PERMISSION_MANAGE_USERS):
            data = {"detail": "You don't have the necessary permission to do this."}
            return Response(data, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def update(self, request: Request, *args, **kwargs):
        if not request.user.has_permission(PERMISSION_MANAGE_USERS):
            data = {"detail": "You don't have the necessary permission to do this."}
            return Response(data, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    @action(
        detail=False, methods=["post"], permission_classes=[], authentication_classes=[]
    )
    def login(self, request: Request):
        serializer = AuthTokenSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user: UserProfile = serializer.validated_data["user"]
        password = serializer.validated_data["password"]

        # check if user active and user accepted in rlc
        if not user.email_confirmed:
            message = "You can not login, yet. Please confirm your email first."
            return Response(
                {"non_field_errors": [message]}, status.HTTP_400_BAD_REQUEST
            )
        if user.locked:
            message = (
                "Your account is temporarily blocked, because your keys need to be recreated. "
                "Please tell an admin to press the unlock button on your user."
            )
            return Response(
                {"non_field_errors": [message]}, status.HTTP_400_BAD_REQUEST
            )
        if hasattr(user, "accepted") and not user.accepted.state == "gr":
            message = (
                "You can not login, yet. Your RLC needs to accept you as a member."
            )
            return Response(
                {"non_field_errors": [message]}, status.HTTP_400_BAD_REQUEST
            )

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
            "users_private_key": private_key,
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="statics/(?P<token>[^/.]+)")
    def statics(self, request: Request, token=None, *args, **kwargs):
        token = Token.objects.get(key=token)
        user = token.user

        notifications = NotificationGroup.objects.filter(user=user, read=False).count()
        user_permissions = [
            model_to_dict(perm) for perm in user.get_all_user_permissions()
        ]
        overall_permissions = [
            model_to_dict(permission) for permission in Permission.objects.all()
        ]
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

    @action(
        detail=False, methods=["post"], authentication_classes=[], permission_classes=[]
    )
    def logout(self, request: Request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_204_NO_CONTENT)
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["get"],
        url_path="activate/(?P<token>[^/.]+)",
        permission_classes=[],
        authentication_classes=[],
    )
    def activate(self, request, token, *args, **kwargs):
        # localhost:4200/activate-account/1023/akoksc-f52702143fcf098155fb1b2c6b081f7a/
        user = self.get_object()
        # user: UserProfile = UserProfile.objects.get(pk=kwargs["pk"])

        if AccountActivationTokenGenerator().check_token(user, token):
            user.email_confirmed = True
            user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            data = {
                "message": "The confirmation link is invalid, possibly because it has already been used."
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get", "post"])
    def inactive(self, request: Request):
        if request.method == "GET":
            if not request.user.has_permission(
                permissions.PERMISSION_ACTIVATE_INACTIVE_USERS_RLC,
                for_rlc=request.user.rlc,
            ):
                raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)

            inactive_users = UserProfile.objects.filter(
                rlc=request.user.rlc, is_active=False
            )
            return Response(UserSerializer(inactive_users, many=True).data)

        elif request.method == "POST":
            if not request.user.has_permission(
                permissions.PERMISSION_ACTIVATE_INACTIVE_USERS_RLC,
                for_rlc=request.user.rlc,
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

    @action(
        detail=False, methods=["POST"], authentication_classes=[], permission_classes=[]
    )
    def password_reset(self, request, *args, **kwargs):
        # get the user
        serializer = UserPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = UserProfile.objects.get(email=serializer.validated_data["email"])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # send the user activation link email
        token = PasswordResetTokenGenerator().make_token(user)
        link = "{}reset-password/{}/{}/".format(settings.FRONTEND_URL, user.id, token)
        subject = "Law & Orga Account Password reset"
        message = "Law & Orga - Reset your password here: {}".format(link)
        html_message = loader.render_to_string(
            "email_templates/reset_password.html", {"link": link}
        )
        send_mail(
            subject=subject,
            html_message=html_message,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        # return the success response
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(
        detail=True, methods=["POST"], authentication_classes=[], permission_classes=[]
    )
    def password_reset_confirm(self, request, *args, **kwargs):
        self.queryset = UserProfile.objects.all()
        user: UserProfile = self.get_object()

        serializer = UserPasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]
        if PasswordResetTokenGenerator().check_token(user, token):
            user.set_password(new_password)
            user.locked = True
            user.save()
            # generate new user private and public key based on the new password
            if hasattr(user, 'encryption_keys'):
                user.encryption_keys.delete()
            user.get_private_key(password_user=new_password)
            # return
            return Response(status=status.HTTP_200_OK)
        else:
            data = {
                "message": "The password reset link is invalid, possibly because it has already been used."
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["POST"])
    def unlock(self, request, pk=None, *args, **kwargs):
        """
        when this api endpoint is called we assume that the public and private key of the submitted user is
        valid and up to date. this means that his private key can be decrypted with the password that this
         user has at the moment.
        """
        user = self.request.user
        user_to_unlock = self.get_object()

        if not request.user.has_permission(
            PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC, for_rlc=user.rlc
        ):
            data = {
                "message": "You need to have the view_records_full_detail permission in order to unlock this user."
                "Because you need to be able to give this user all his encryption keys."
            }
            return Response(data)

        # generate new rlc key
        private_key_user = request.user.get_private_key(request=request)
        request.user.generate_keys_for_user(private_key_user, user_to_unlock)

        # unlock the user
        user_to_unlock.locked = False
        user_to_unlock.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
