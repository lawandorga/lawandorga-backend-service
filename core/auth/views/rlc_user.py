from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.models import PasswordResetTokenGenerator, RlcUser, UserProfile
from core.seedwork.permission import CheckPermissionWall
from core.static import PERMISSION_ADMIN_MANAGE_USERS

from ..serializers import (
    ChangePasswordSerializer,
    EmailSerializer,
    RlcUserForeignSerializer,
    RlcUserSerializer,
    RlcUserUpdateSerializer,
    UserPasswordResetConfirmSerializer,
)
from ..token_generator import EmailConfirmationTokenGenerator


class RlcUserViewSet(
    CheckPermissionWall,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
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
        super().perform_authentication(request)

    def get_permissions(self):
        if self.action in [
            "statics",
            "logout",
            "password_reset",
            "password_reset_confirm",
            "activate",
        ]:
            return []
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ["list"]:
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
            "unlock",
            "destroy",
            "permissions",
            "update",
            "partial_update",
            "change_password",
        ]:
            queryset = RlcUser.objects.filter(org=self.request.user.rlc_user.org)
        else:
            queryset = RlcUser.objects.filter(pk=self.request.user.rlc_user.id)
        return queryset

    @action(detail=False, methods=["post"])
    def change_password(self, request: Request):
        user: UserProfile = self.request.user  # type: ignore
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user.change_password(
            serializer.validated_data["current_password"],
            serializer.validated_data["new_password"],
        )
        return Response(RlcUserSerializer(user.rlc_user).data)

    @action(detail=False, methods=["get"])
    def dashboard(self, request, *args, **kwargs):
        user = request.user
        return Response(user.get_information())

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

        if EmailConfirmationTokenGenerator().check_token(rlc_user, token):
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
        rlc_user: RlcUser = self.get_object()

        serializer = UserPasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]
        user = rlc_user.user
        if PasswordResetTokenGenerator().check_token(user, token):
            user.set_password(new_password)
            rlc_user.generate_keys(new_password)
            rlc_user.locked = True
            with transaction.atomic():
                user.save()
                rlc_user.save()
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
