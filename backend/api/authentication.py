#  rlcapp - record and organization management software for refugee law clinics
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

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from datetime import datetime
import pytz
from django.conf import settings


class ExpiringTokenAuthentication(TokenAuthentication):
    model = Token

    def authenticate_credentials(self, key):
        try:
            token = Token.objects.get(key=key)
        except self.model.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or deleted')

        utc_now = datetime.utcnow().replace(tzinfo=pytz.timezone(settings.TIME_ZONE))

        if (token.created < (utc_now - settings.TIMEOUT_TIMEDELTA)) and not token.user.is_superuser:
            token.delete()
            raise AuthenticationFailed('Token has expired')

        token.created = datetime.utcnow().replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
        token.save()
        token.user.last_login = datetime.utcnow().replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
        token.user.save()
        return token.user, token


