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

from rest_framework import status, serializers
from rest_framework.exceptions import APIException
from django.utils.encoding import force_text


class EntryAlreadyExistingError(serializers.ValidationError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'the entry which was tried to create, existed already in the database'


class CustomError(APIException):
    status_code = 400
    default_code = 'rlc_app.custom_error'
    default_detail = 'base error, should be specified'

    def __init__(self, detail):
        if isinstance(detail, dict):
            if 'error_detail' in detail:
                self.detail = detail['error_detail']
            if 'error_code' in detail:
                self.default_code = detail['error_code']
        elif detail is not None:
            self.detail = {'detail': force_text(detail)}
        else:
            self.detail = {'detail': force_text(self.default_detail)}
