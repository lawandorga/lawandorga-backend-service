from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed, ParseError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from apps.api.models import (
    AccountActivationTokenGenerator,
    PasswordResetTokenGenerator,
    RlcUser,
    UserProfile,
    UsersRlcKeys,
)
from apps.api.serializers import (
    ChangePasswordSerializer,
    EmailSerializer,
    RlcSerializer,
    RlcUserCreateSerializer,
    RlcUserForeignSerializer,
    RlcUserJWTSerializer,
    RlcUserSerializer,
    RlcUserUpdateSerializer,
    UserPasswordResetConfirmSerializer,
)
from apps.api.static import (
    PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS,
    PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS,
    PERMISSION_ADMIN_MANAGE_USERS,
)
from apps.recordmanagement.models import RecordAccess, RecordDeletion
from apps.static.permission import CheckPermissionWall


class RlcUserViewSet(CheckPermissionWall, viewsets.ModelViewSet):
    serializer_class = RlcUserSerializer
    queryset = RlcUser.objects.none()
    permission_wall = {
        "destroy": PERMISSION_ADMIN_MANAGE_USERS,
        "accept": PERMISSION_ADMIN_MANAGE_USERS,
    }

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.check_delete_is_safe():
            raise ParseError(
                "You can not delete this user right now, because you could loose access to one or "
                "more records. This user is one of the two only persons with access to those records."
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_authentication(self, request):
        if self.action in ["login", "refresh"]:
            pass
        else:
            super().perform_authentication(request)

    def get_permissions(self):
        if self.action in [
            "statics",
            "create",
            "logout",
            "login",
            "password_reset",
            "password_reset_confirm",
            "activate",
            "refresh",
        ]:
            return []
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ["create"]:
            return RlcUserCreateSerializer
        elif self.action in ["list"]:
            return RlcUserForeignSerializer
        elif self.action in ["update", "partial_update"]:
            return RlcUserUpdateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.action in ["activate", "password_reset_confirm"]:
            queryset = RlcUser.objects.all()
        elif self.action in [
            "list",
            "retrieve",
            "accept",
            "unlock",
            "destroy",
            "permissions",
            "update",
            "partial_update",
            "change_password",
        ]:
            queryset = RlcUser.objects.filter(user__rlc=self.request.user.rlc)
        else:
            queryset = RlcUser.objects.filter(pk=self.request.user.rlc_user.id)
        group = self.request.query_params.get("group", None)
        if group:
            group = self.request.user.rlc.group_from_rlc.get(
                pk=group
            ).group_members.values_list("rlc_user__pk", flat=True)
            queryset = queryset.filter(pk__in=group)
        return queryset

    def retrieve(self, request, pk=None, **kwargs):
        rlc_user = self.get_object()
        if (
            request.user.has_permission(PERMISSION_ADMIN_MANAGE_USERS)
            or rlc_user.pk == request.user.rlc_user.pk
        ):
            serializer = RlcUserSerializer(rlc_user)
        else:
            serializer = RlcUserForeignSerializer(rlc_user)
        return Response(serializer.data)

    def update(self, request: Request, *args, **kwargs):
        rlc_user = self.get_object()
        if request.user.rlc_user.pk != rlc_user.pk and not request.user.has_permission(
            PERMISSION_ADMIN_MANAGE_USERS
        ):
            data = {
                "detail": "You need the permission {} to do this.".format(
                    PERMISSION_ADMIN_MANAGE_USERS
                )
            }
            return Response(data, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(rlc_user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(RlcUserSerializer(rlc_user).data)

    @action(detail=False, methods=["post"])
    def change_password(self, request: Request):
        user = self.request.user
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user.change_password(
            serializer.validated_data["current_password"],
            serializer.validated_data["new_password"],
        )
        return Response(RlcUserSerializer(user.rlc_user).data)

    @action(detail=False, methods=["post"])
    def refresh(self, request):
        serializer = TokenRefreshSerializer(
            data=request.data, context={"request": request}
        )

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def login(self, request: Request):
        serializer = RlcUserJWTSerializer(
            data=request.data, context={"request": request}
        )

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        except AuthenticationFailed:
            raise ParseError(
                {
                    "non_field_errors": [
                        "This e-mail doesn't exist or the password is wrong."
                    ]
                }
            )
        user = serializer.user
        # password = serializer.validated_data["password"]

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
                "You can not login. Your account was deactivated by one of your admins."
            )
            return Response(
                {"non_field_errors": [message]}, status.HTTP_400_BAD_REQUEST
            )
        if not user.rlc_user.accepted:
            message = "You can not login, yet. You need to be accepted as member by one of your admins."
            return Response(
                {"non_field_errors": [message]}, status.HTTP_400_BAD_REQUEST
            )

        # return
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def dashboard(self, request, *args, **kwargs):
        user = request.user
        return Response(user.get_information())

    @action(detail=False, methods=["get"])
    def admin(self, request, *args, **kwargs):
        instance = request.user
        if instance.has_permission(PERMISSION_ADMIN_MANAGE_USERS):
            profiles = UserProfile.objects.filter(
                Q(rlc=instance.rlc)
                & (Q(rlc_user__locked=True) | Q(rlc_user__accepted=False))
            ).count()
        else:
            profiles = 0
        if instance.has_permission(PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS):
            record_deletion_requests = RecordDeletion.objects.filter(
                record__template__rlc=instance.rlc, state="re"
            ).count()
        else:
            record_deletion_requests = 0
        if instance.has_permission(PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS):
            record_permit_requests = RecordAccess.objects.filter(
                record__template__rlc=instance.rlc, state="re"
            ).count()
        else:
            record_permit_requests = 0
        data = {
            "profiles": profiles,
            "record_deletion_requests": record_deletion_requests,
            "record_permit_requests": record_permit_requests,
        }
        return Response(data)

    @action(detail=False, methods=["get"])
    def statics(self, request):
        try:
            payload = request.auth.payload
        except AttributeError:
            raise ParseError("Token was not set within the request.")
        user = UserProfile.objects.get(pk=payload["django_user"])

        data = {
            "user": RlcUserSerializer(user.rlc_user).data,
            "rlc": RlcSerializer(user.rlc).data,
            "permissions": user.get_all_user_permissions(),
        }

        return Response(data, status=status.HTTP_200_OK)

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
            if hasattr(user, "encryption_keys"):
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
            data = {"detail": "You can not unlock yourself. This does not work."}
            return Response(data, status=status.HTTP_403_FORBIDDEN)

        # generate new rlc key
        private_key_user = request.user.get_private_key(request=request)
        success = request.user.generate_keys_for_user(private_key_user, user_to_unlock)

        # unlock the user if all keys were generated
        if success:
            rlc_user.locked = False
            rlc_user.save()
            return Response(RlcUserSerializer(rlc_user).data)
        else:
            raise ParseError(
                "Not all keys could be handed over. Please tell another admin to unlock this user."
            )

    @action(detail=True, methods=["post"])
    def accept(self, request, *args, **kwargs):
        if not request.user.has_permission(PERMISSION_ADMIN_MANAGE_USERS):
            return Response(
                {
                    "detail": "You don't have the necessary permission '{}' to do this.".format(
                        PERMISSION_ADMIN_MANAGE_USERS
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # get the new member
        new_member = self.get_object()

        # create the rlc encryption keys for new member
        private_key_user = request.user.get_private_key(request=request)
        aes_key_rlc = request.user.rlc.get_aes_key(
            user=request.user, private_key_user=private_key_user
        )
        new_user_rlc_keys = UsersRlcKeys(
            user=new_member.user,
            rlc=request.user.rlc,
            encrypted_key=aes_key_rlc,
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
        return Response(RlcUserSerializer(instance=new_member).data)
