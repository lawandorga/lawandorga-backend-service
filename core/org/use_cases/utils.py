from datetime import timedelta

from django.utils import timezone

from core.auth.models import OrgUser
from core.seedwork.use_case_layer.error import UseCaseError


def check_user_is_not_an_old_one(user: OrgUser):
    one_year_ago = timezone.now() - timedelta(days=365)
    user_created_more_than_one_year_ago = user.user.created < one_year_ago
    last_login_more_than_one_year_ago = (
        user.user.last_login is None or user.user.last_login < one_year_ago
    )
    if user_created_more_than_one_year_ago and last_login_more_than_one_year_ago:
        raise UseCaseError(
            "The user registered more than one year ago and has not logged in since. "
            "Therefore this action is not allowed. "
            "You might want to delete this user instead or tell the user to login again."
        )
