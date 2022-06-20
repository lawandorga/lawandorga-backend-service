from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken


class IsAuthenticatedAndEverything(permissions.IsAuthenticated):
    message = (
        "You need to be logged in, your account needs to be active, your email needs to be confirmed, your"
        "account should not be locked and you should be accepted as a member of your law clinic."
    )

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        # get the user
        user = request.user

        # rlc user
        if hasattr(user, "rlc_user"):
            rlc_user = user.rlc_user
            if (
                not rlc_user.is_active
                or not rlc_user.email_confirmed
                or not user.rlc_user.accepted
                or user.rlc_user.locked
            ):
                return False

        # statistic user
        if hasattr(user, "statistic_user"):
            pass

        # default
        return True


class RefreshPrivateKeyToken(RefreshToken):
    @classmethod
    def for_user(cls, user, password_user=None, private_key=None):
        if password_user:
            key = user.get_private_key(password_user=password_user)
        elif private_key:
            key = private_key
        else:
            raise ValueError("You need to pass (password_user) or (private_key).")
        token = super().for_user(user)
        token["key"] = key
        return token
