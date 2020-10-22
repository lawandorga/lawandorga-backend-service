#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2020  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>

from rest_framework.request import Request
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from backend.api.models import UserSession
from backend.static.encryption import get_bytes_from_string_or_return_bytes
from backend.api.errors import CustomError
from backend.static.error_codes import ERROR__API__USER__NO_PRIVATE_KEY_PROVIDED
from backend.static.encryption import get_string_from_bytes_or_return_string
from backend.static.metrics import Metrics


def get_private_key_from_request(request):
    private_key = request.META.get("HTTP_PRIVATE_KEY")
    if not private_key:
        raise CustomError(ERROR__API__USER__NO_PRIVATE_KEY_PROVIDED)
    private_key = get_string_from_bytes_or_return_string(private_key)
    if "\\n" in private_key:
        private_key = private_key.replace("\\n", "\n")
    if "<linebreak>" in private_key:
        private_key = private_key.replace("<linebreak>", "\n")

    if isinstance(private_key, str):
        private_key = get_bytes_from_string_or_return_bytes(private_key)
    return private_key


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request: Request):
        if request.path.find("metrics") != -1:
            timeframe = timezone.now() - timedelta(minutes=5)

            active_users = (
                UserSession.objects.filter(end_time__gt=timeframe)
                .values("user")
                .distinct()
                .count()
            )
            Metrics.currently_active_users.set(active_users)

        response: Response = self.get_response(request)

        if (
            request.path.find("unread_notifications") == -1
            and request.path.find("login") == -1
            and request.path.find("user_has_permissions") == -1
        ):
            UserSession.objects.log_user_activity(
                request.user, str(request.path), str(request.method)
            )
        return response
