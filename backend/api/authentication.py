#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
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
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.utils import timezone


class ExpiringTokenAuthentication(TokenAuthentication):
    model = Token

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)

        if user.last_login and user.last_login < (timezone.now() - settings.TIMEOUT_TIMEDELTA):
            token.delete()
            raise AuthenticationFailed("Token has expired.")

        user.last_login = timezone.now()
        user.save()

        return user, token
