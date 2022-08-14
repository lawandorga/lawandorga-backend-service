from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed, ParseError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from apps.core.models import StatisticUser
from apps.core.serializers import (
    ChangePasswordSerializer,
    StatisticUserJWTSerializer,
    StatisticUserSerializer,
)


class StatisticsUserViewSet(viewsets.GenericViewSet):
    serializer_class = StatisticUserSerializer
    queryset = StatisticUser.objects.none()

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

    def get_queryset(self):
        queryset = StatisticUser.objects.filter(pk=self.request.user.statistic_user.id)
        return queryset

    @action(detail=False, methods=["post"])
    def login(self, request: Request):
        # check login
        serializer = StatisticUserJWTSerializer(
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

        # check if user active and user accepted in rlc
        if not hasattr(user, "statistic_user"):
            message = "You are not allowed to login here. You need to have the statistics user role."
            return Response(
                {"non_field_errors": [message]}, status.HTTP_400_BAD_REQUEST
            )

        # return
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

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

    @action(detail=False, methods=["get"])
    def statics(self, request):
        instance = self.request.user

        data = {
            "user": StatisticUserSerializer(instance.statistic_user).data,
        }

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def change_password(self, request: Request):
        user: UserProfile = self.request.user  # type: ignore
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        try:
            user.statistic_user.change_password(
                serializer.validated_data["current_password"],
                serializer.validated_data["new_password"],
            )
        except ValueError as e:
            raise ParseError(str(e))
        return Response(StatisticUserSerializer(user.statistic_user).data)
