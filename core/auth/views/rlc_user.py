from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.auth.serializers import (
    ChangePasswordSerializer,
    RlcUserForeignSerializer,
    RlcUserSerializer,
    RlcUserUpdateSerializer,
)
from core.models import RlcUser, UserProfile


class RlcUserViewSet(
    GenericViewSet,
):
    serializer_class = RlcUserSerializer
    queryset = RlcUser.objects.none()

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
        if self.action in [
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
