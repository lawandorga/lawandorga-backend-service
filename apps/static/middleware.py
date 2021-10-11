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
from rest_framework.response import Response
from apps.api.models import LoggedPath


def get_private_key_from_request(request):
    return request.user.get_private_key(request=request)


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # get the response
        response: Response = self.get_response(request)

        # log which endpoint is called
        user = request.user
        if not request.user.is_authenticated:
            user = None
        LoggedPath.objects.create(user=user, path=request.path)

        # return the response
        return response
