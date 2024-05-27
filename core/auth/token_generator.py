from datetime import datetime
from typing import TYPE_CHECKING

from django.conf import settings
from django.utils.crypto import salted_hmac
from django.utils.http import base36_to_int, int_to_base36

if TYPE_CHECKING:
    from core.auth.models import OrgUser


class EmailConfirmationTokenGenerator:
    key_salt = "EmailConfirmationTokenGenerator"
    timeout = 60 * 60 * 24 * 30 * 12  # 12 months

    def make_token(self, user: "OrgUser"):
        return self._make_token_with_timestamp(
            user,
            self._num_seconds(self._now()),
        )

    def check_token(self, user: "OrgUser", token: str):
        """
        Check that a password reset token is correct for a given user.
        """
        if not (user and token):
            return False
        # Parse the token
        try:
            ts_b36, _ = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check the token is valid
        check_token = self._make_token_with_timestamp(user, ts)
        if token != check_token:
            return False

        # Check the timestamp is within limit.
        if (self._num_seconds(self._now()) - ts) > self.timeout:
            return False

        return True

    def _make_token_with_timestamp(self, user: "OrgUser", timestamp: int):
        # timestamp is number of seconds since 2001-1-1. Converted to base 36,
        # this gives us a 6 digit string until about 2069.
        ts_b36 = int_to_base36(timestamp)
        hash_string = salted_hmac(
            self.key_salt,
            self._make_hash_value(user, timestamp),
            secret=settings.SECRET_KEY,
            algorithm="sha256",
        ).hexdigest()[::2]
        return "%s-%s" % (ts_b36, hash_string)

    def _make_hash_value(self, user: "OrgUser", timestamp: int):
        return f"{user.pk}{user.user.email}{user.email_confirmed}{timestamp}"

    def _num_seconds(self, dt):
        return int((dt - datetime(2001, 1, 1)).total_seconds())

    def _now(self):
        return datetime.now()
