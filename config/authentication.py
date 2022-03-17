from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions


class IsAuthenticatedAndEverything(permissions.IsAuthenticated):
    message = 'You need to be logged in, your account needs to be active, your email needs to be confirmed, your' \
              'account should not be locked and you should be accepted as a lc member.'

    def has_permission(self, request, view):
        return (
            super().has_permission(request, view) and
            request.user.rlc_user.is_active and
            request.user.rlc_user.email_confirmed and
            not request.user.rlc_user.locked and
            request.user.rlc_user.accepted
        )


class RefreshPrivateKeyToken(RefreshToken):
    @classmethod
    def for_user(cls, user, password_user=None, private_key=None):
        if password_user:
            private_key = user.get_private_key(password_user=password_user)
        elif private_key:
            private_key = private_key
        else:
            raise ValueError('You need to pass (password_user) or (private_key).')
        token = super().for_user(user)
        token['key'] = private_key
        return token
