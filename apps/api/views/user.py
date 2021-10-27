from rest_framework.authtoken.models import Token
from apps.api.models.permission import Permission
from apps.recordmanagement.models import EncryptedRecordDeletionRequest, EncryptedRecordPermission
from apps.static.permissions import PERMISSION_MANAGE_USERS, PERMISSION_PROCESS_RECORD_DELETION_REQUESTS, \
    PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC, PERMISSION_MANAGE_PERMISSIONS_RLC
from rest_framework.exceptions import ParseError, PermissionDenied, AuthenticationFailed
from rest_framework.decorators import action
from apps.api.serializers import (
    RlcUserCreateSerializer,
    RlcUserForeignSerializer,
    EmailSerializer,
    UserPasswordResetConfirmSerializer, HasPermissionAllNamesSerializer, RlcSerializer, RlcUserSerializer,
    AuthTokenSerializer, UserProfileNameSerializer, RlcUserListSerializer, RlcUserUpdateSerializer,
    UserProfileSerializer,
)
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.request import Request
from django.forms.models import model_to_dict
from apps.api.models import (
    UserProfile,
    NotificationGroup,
    PasswordResetTokenGenerator,
    AccountActivationTokenGenerator, UsersRlcKeys, RlcUser,
)
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import viewsets, status
from django.utils import timezone
from django.db import IntegrityError


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = RlcUserSerializer
    queryset = RlcUser.objects.none()

    def get_permissions(self):
        if self.action in ['statics', 'create', 'logout', 'login', 'password_reset', 'password_reset_confirm',
                           'activate']:
            return []
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ["create"]:
            return RlcUserCreateSerializer
        elif self.action in ['list']:
            return RlcUserListSerializer
        elif self.action in ['update', 'partial_update']:
            return RlcUserUpdateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.action in ['activate', 'password_reset_confirm']:
            return RlcUser.objects.all()
        elif self.action in ['list', 'retrieve', 'accept', 'unlock', 'destroy', 'permissions', 'update',
                             'partial_update']:
            return RlcUser.objects.filter(user__rlc=self.request.user.rlc)
        return RlcUser.objects.filter(pk=self.request.user.rlc_user.id)

    def retrieve(self, request, pk=None, **kwargs):
        rlc_user = self.get_object()
        if request.user.has_permission(PERMISSION_MANAGE_USERS) or rlc_user.pk == request.user.rlc_user.pk:
            serializer = RlcUserListSerializer(rlc_user)
        else:
            serializer = RlcUserForeignSerializer(rlc_user)
        return Response(serializer.data)

    def update(self, request: Request, *args, **kwargs):
        rlc_user = self.get_object()
        if not request.user.has_permission(PERMISSION_MANAGE_USERS) and request.user.rlc_user.pk != rlc_user.pk:
            data = {"detail": "You don't have the necessary permission to do this."}
            return Response(data, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(rlc_user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(RlcUserListSerializer(rlc_user).data)

    def destroy(self, request, *args, **kwargs):
        rlc_user = self.get_object()
        if not request.user.has_permission(PERMISSION_MANAGE_USERS) and request.user.rlc_user.pk != rlc_user.pk:
            data = {"detail": "You don't have the necessary permission to do this."}
            return Response(data, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(rlc_user.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=["post"], permission_classes=[], authentication_classes=[]
    )
    def login(self, request: Request):
        serializer = AuthTokenSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user: UserProfile = serializer.validated_data["user"]
        password = serializer.validated_data["password"]

        # check if user active and user accepted in rlc
        if not user.rlc_user.email_confirmed:
            message = "You can not login, yet. Please confirm your email first."
            return Response(
                {"non_field_errors": [message]}, status.HTTP_400_BAD_REQUEST
            )
        if user.rlc_user.locked:
            message = (
                "Your account is temporarily blocked, because your keys need to be recreated. "
                "Please tell an admin to press the unlock button on your user."
            )
            return Response(
                {"non_field_errors": [message]}, status.HTTP_400_BAD_REQUEST
            )
        if not user.rlc_user.is_active:
            message = (
                "You can not login. Your account was deactivated by one of your rlc admins."
            )
            return Response(
                {"non_field_errors": [message]}, status.HTTP_400_BAD_REQUEST
            )
        if not user.rlc_user.accepted:
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
        private_key = user.get_private_key(password_user=password)

        # build the response
        data = {
            "token": token.key,
            "key": private_key,
            "user": UserProfileSerializer(user).data,
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def admin(self, request, *args, **kwargs):
        instance = request.user
        if instance.has_permission(PERMISSION_MANAGE_USERS):
            profiles = UserProfile.objects.filter(
                Q(rlc=instance.rlc) & (Q(rlc_user__locked=True) | Q(rlc_user__accepted=False))).count()
        else:
            profiles = 0
        if instance.has_permission(PERMISSION_PROCESS_RECORD_DELETION_REQUESTS):
            record_deletion_requests = EncryptedRecordDeletionRequest.objects.filter(record__from_rlc=instance.rlc,
                                                                                     state='re').count()
        else:
            record_deletion_requests = 0
        if instance.has_permission(PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC):
            record_permit_requests = EncryptedRecordPermission.objects.filter(record__from_rlc=instance.rlc,
                                                                              state='re').count()
        else:
            record_permit_requests = 0
        data = {
            'profiles': profiles,
            'record_deletion_requests': record_deletion_requests,
            'record_permit_requests': record_permit_requests
        }
        return Response(data)

    @action(detail=False, methods=["get"], url_path="statics/(?P<token>[^/.]+)")
    def statics(self, request: Request, token=None, *args, **kwargs):
        try:
            token = Token.objects.get(key=token)
        except ObjectDoesNotExist:
            raise AuthenticationFailed("Your token doesn't exist, please login again.")
        user = token.user

        notifications = NotificationGroup.objects.filter(user=user, read=False).count()
        overall_permissions = [
            model_to_dict(permission) for permission in Permission.objects.all()
        ]

        data = {
            "user": UserProfileSerializer(user).data,
            "rlc": RlcSerializer(user.rlc).data,
            "notifications": notifications,
            "permissions": user.get_all_user_permissions(),
            "all_permissions": overall_permissions,
        }

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def logout(self, request: Request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_204_NO_CONTENT)
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post"],
        url_path="activate/(?P<token>[^/.]+)",
        permission_classes=[],
        authentication_classes=[],
    )
    def activate(self, request, token, *args, **kwargs):
        # localhost:4200/activate-account/1023/akoksc-f52702143fcf098155fb1b2c6b081f7a/
        rlc_user = self.get_object()

        if AccountActivationTokenGenerator().check_token(rlc_user, token):
            rlc_user.email_confirmed = True
            rlc_user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            data = {
                "detail": "The confirmation link is invalid, possibly because it has already been used."
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False, methods=["POST"], authentication_classes=[], permission_classes=[]
    )
    def password_reset(self, request, *args, **kwargs):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = UserProfile.objects.get(email=serializer.validated_data["email"])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user.rlc_user.send_password_reset_email()
        return Response()

    @action(
        detail=True, methods=["POST"], authentication_classes=[], permission_classes=[]
    )
    def password_reset_confirm(self, request, *args, **kwargs):
        rlc_user = self.get_object()

        serializer = UserPasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]
        user = rlc_user.user
        if PasswordResetTokenGenerator().check_token(user, token):
            user.set_password(new_password)
            user.save()
            rlc_user.locked = True
            rlc_user.save()
            # generate new user private and public key based on the new password
            if hasattr(user, 'encryption_keys'):
                user.encryption_keys.delete()
            # get the user from db because the old encryption_keys might still be in this user
            user = UserProfile.objects.get(pk=rlc_user.user.pk)
            user.get_private_key(password_user=new_password)
            # return
            return Response(status=status.HTTP_200_OK)
        else:
            data = {
                "detail": "The password reset link is invalid, possibly because it has already been used."
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
        rlc_user = self.get_object()
        user_to_unlock = rlc_user.user

        if user == user_to_unlock:
            data = {
                'detail': 'You can not unlock yourself. This does not work.'
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        # generate new rlc key
        private_key_user = request.user.get_private_key(request=request)
        success = request.user.generate_keys_for_user(private_key_user, user_to_unlock)

        # unlock the user if all keys were generated
        if success:
            rlc_user.locked = False
            rlc_user.save()
            return Response(RlcUserListSerializer(rlc_user).data)
        else:
            raise ParseError('Not all keys could be handed over. Please tell another admin to unlock this user.')

    @action(detail=True, methods=['GET'])
    def permissions(self, request, *args, **kwargs):
        rlc_user = self.get_object()
        if request.user.has_permission(PERMISSION_MANAGE_PERMISSIONS_RLC):
            user_permissions = rlc_user.user.get_permissions()
        else:
            raise PermissionDenied(
                "You need the permission 'manage_permissions_rlc' to see the permissions of this user")
        return Response(HasPermissionAllNamesSerializer(user_permissions, many=True).data)

    @action(detail=True, methods=['post'])
    def accept(self, request, *args, **kwargs):
        # get the new member
        new_member = self.get_object()

        # create the rlc encryption keys for new member
        private_key_user = request.user.get_private_key(request=request)
        aes_key_rlc = request.user.rlc.get_aes_key(
            user=request.user, private_key_user=private_key_user
        )
        new_user_rlc_keys = UsersRlcKeys(
            user=new_member.user, rlc=request.user.rlc, encrypted_key=aes_key_rlc,
        )
        public_key = new_member.user.get_public_key()
        new_user_rlc_keys.encrypt(public_key)

        # set the user accepted field so that the user can login
        new_member.accepted = True
        new_member.save()

        # save the rlc keys this is here and not before the previous block so that test_accept_works doesnt complain
        try:
            new_user_rlc_keys.save()
        except IntegrityError:
            # this happens when the keys exist already for whatever reason
            pass

        # return
        return Response(RlcUserListSerializer(instance=new_member).data)
