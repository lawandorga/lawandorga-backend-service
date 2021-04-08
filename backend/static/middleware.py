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
from backend.api.models.user_session import UserSession
from rest_framework.response import Response
from rest_framework.request import Request
from backend.api.models.rlc import Rlc
from backend.static.metrics import Metrics
from django.db.models import Count
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta


def get_private_key_from_request(request):
    return request.user.get_private_key(request=request)


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: Request):
        # if request.path.find("metrics") != -1:
        #     timeframe = timezone.now() - timedelta(seconds=15)
        #
        #     active_users = (
        #         UserSession.objects.filter(end_time__gt=timeframe)
        #         .values("user")
        #         .distinct()
        #         .count()
        #     )
        #     Metrics.currently_active_users.set(active_users)
        #
        #     recent_user_sessions = Count(
        #         "user_sessions", filter=Q(user_sessions__end_time__gt=timeframe)
        #     )
        #     rlcs = Rlc.objects.annotate(sessions=recent_user_sessions).values(
        #         "id", "name", "sessions"
        #     )
        #     listed_rlcs = list(rlcs)
        #
        #     for rlc in listed_rlcs:
        #         Metrics.currently_active_users_per_rlc.labels(rlc_name=rlc["name"]).set(
        #             rlc["sessions"]
        #         )

        response: Response = self.get_response(request)

        # if (
        #     request.path.find("unread_notifications") == -1
        #     and request.path.find("login") == -1
        #     and request.path.find("user_has_permissions") == -1
        #     and request.path.find("metrics") == -1
        # ):
        #     UserSession.objects.log_user_activity(
        #         request.user, str(request.path), str(request.method)
        #     )
        return response
