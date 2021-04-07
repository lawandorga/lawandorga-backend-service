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
from backend.api.models.user_activity_path import UserActivityPath
from backend.api.models.user_session import UserSession
from backend.static.error_codes import ERROR__API__LOGGING__TOO_MANY_SESSION_PATHS_FOUND
from backend.api.errors import CustomError
from django.db import models


class UserSessionPathManager(models.Manager):
    @staticmethod
    def log_path(session: UserSession, path: str):
        path_object = UserActivityPath.objects.get_or_create(path=path)[0]
        existing = UserSessionPath.objects.filter(session=session, path=path_object)
        existing_counter = existing.count()
        if existing_counter == 1:
            session_path: UserSessionPath = existing.first()
            session_path.counter = session_path.counter + 1
            session_path.save()
        elif existing_counter > 1:
            raise CustomError(ERROR__API__LOGGING__TOO_MANY_SESSION_PATHS_FOUND)
        else:
            session_path: UserSessionPath = UserSessionPath(
                path=path_object, counter=1, session=session
            )
            session_path.save()


class UserSessionPath(models.Model):
    path = models.ForeignKey(
        UserActivityPath,
        related_name="sessions_paths",
        on_delete=models.CASCADE,
        null=False,
    )
    session = models.ForeignKey(
        UserSession,
        related_name="sessions_paths",
        on_delete=models.CASCADE,
        null=False,
    )
    counter = models.IntegerField(default=1)

    objects = UserSessionPathManager()

    class Meta:
        verbose_name = "UserSessionPath"
        verbose_name_plural = "UserSessionPaths"

    def __str__(self):
        return "userSessionPath: {};".format(self.pk)
