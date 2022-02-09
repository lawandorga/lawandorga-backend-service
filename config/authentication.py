from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import permissions
from django.utils import timezone
from django.conf import settings


class ExpiringTokenAuthentication(TokenAuthentication):
    model = Token

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)

        if (
            (user.last_login and user.last_login < (timezone.now() - settings.TIMEOUT_TIMEDELTA)) and
            (token.created < (timezone.now() - settings.TIMEOUT_TIMEDELTA))
        ):
            token.delete()
            raise AuthenticationFailed("Token has expired.")

        user.last_login = timezone.now()
        user.save()

        return user, token


class IsAuthenticatedAndActive(permissions.IsAuthenticated):
    message = 'You need to be logged in and your account needs to be active.'

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.rlc_user.is_active
