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

from django.db import models
from django.utils import timezone
from datetime import timedelta
from django_prometheus.models import ExportModelOperationsMixin
import logging

from backend.api.models import Rlc, UserProfile


class UserSessionManager(models.Manager):
    @staticmethod
    def log_user_activity(user: UserProfile, path: str, method: str) -> None:
        if not user.is_authenticated:
            pseudo_user = "anonymous"
            rlc = None
        else:
            pseudo_user = str(hash(str(user.id) + user.email))
            rlc = user.rlc

        now = timezone.now()
        before = now - timedelta(minutes=20)

        existing = UserSession.objects.filter(end_time__gt=before, user=pseudo_user)
        existing_count = existing.count()
        if existing_count >= 1:
            session: UserSession = existing.first()
            session.end_time = now
            session.save()
        else:
            session: UserSession = UserSession(
                user=pseudo_user, rlc=rlc, end_time=now, start_time=now
            )
            session.save()
        from backend.api.models import UserSessionPath

        complete_path = method + " " + path

        logger = logging.getLogger(__name__)
        logger.debug("logging complete path: " + complete_path)
        UserSessionPath.objects.log_path(session=session, path=complete_path)


class UserSession(ExportModelOperationsMixin("user_session"), models.Model):
    user = models.CharField(
        max_length=255, null=False
    )  # no connection to user on purpose (for privacy)
    rlc = models.ForeignKey(
        Rlc,
        related_name="user_sessions",
        on_delete=models.SET_NULL,
        null=True,
        default=None,
    )
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)

    objects = UserSessionManager()
