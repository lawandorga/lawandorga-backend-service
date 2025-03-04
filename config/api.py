from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest

from core.auth.models import OrgUser, StatisticUser, UserProfile
from core.mail.models import MailUser
from core.seedwork.api_layer import ApiError

not_authenticated_error = ApiError(
    message="You need to be logged in.",
    status=401,
)


def get_anonymous_user(request: HttpRequest) -> AnonymousUser:
    if isinstance(request.user, AnonymousUser):
        return request.user
    return AnonymousUser()


def get_user(request: HttpRequest) -> UserProfile:
    if not request.user.is_authenticated:
        raise not_authenticated_error

    return UserProfile.objects.get(pk=request.user.pk)


def get_mail_user(request: HttpRequest) -> MailUser:
    if not request.user.is_authenticated:
        raise not_authenticated_error

    user: UserProfile = request.user  # type: ignore
    if not hasattr(user, "mail_user"):
        raise ApiError(
            message="Mail User Required",
            detail="You need to have the mail user role.",
            status=403,
        )

    mail_user = user.mail_user
    mail_user.check_login_allowed()
    return mail_user


def get_org_user(request: HttpRequest) -> OrgUser:
    if not request.user.is_authenticated:
        raise not_authenticated_error

    user: UserProfile = request.user  # type: ignore
    if not hasattr(user, "org_user"):
        raise ApiError(
            message="Org User Required",
            detail="You need to have the org user role.",
            status=403,
        )

    org_user = user.org_user
    org_user.check_login_allowed()
    return org_user


def get_statistics_user(request: HttpRequest) -> StatisticUser:
    if not request.user.is_authenticated:
        raise not_authenticated_error

    user: UserProfile = request.user  # type: ignore
    if not hasattr(user, "statistic_user"):
        raise ApiError(
            message="Statistics User Required",
            detail="You need to have the statistics user role.",
            status=403,
        )

    statistics_user = user.statistic_user
    statistics_user.check_login_allowed()
    return statistics_user
