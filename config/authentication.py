from rest_framework import exceptions, permissions, status, views


class IsAuthenticatedAndEverything(permissions.IsAuthenticated):  # type: ignore
    message = (
        "You need to be logged in, your account needs to be active, "
        "your email needs to be confirmed, your"
        "account should not be locked and you should be "
        "accepted as a member of your law clinic."
    )

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        # get the user
        user = request.user

        # org user
        if hasattr(user, "org_user"):
            org_user = user.org_user
            if (
                not org_user.is_active
                or not org_user.email_confirmed
                or not user.org_user.accepted
            ):
                return False

        # statistic user
        if hasattr(user, "statistic_user"):
            pass

        # default
        return True


def custom_exception_handler(exc, context):
    response = views.exception_handler(exc, context)

    if isinstance(exc, (exceptions.AuthenticationFailed, exceptions.NotAuthenticated)):
        response.status_code = status.HTTP_401_UNAUTHORIZED

    return response
