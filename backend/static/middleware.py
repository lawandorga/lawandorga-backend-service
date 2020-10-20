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

from django.utils import timezone
from rest_framework.request import Request
from rest_framework.response import Response

from backend.static.encryption import get_bytes_from_string_or_return_bytes
from backend.api.errors import CustomError
from backend.static.error_codes import ERROR__API__USER__NO_PRIVATE_KEY_PROVIDED
from backend.static.encryption import get_string_from_bytes_or_return_string


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
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response: Response = self.get_response(request)
        print("\n")

        # print("logging")
        # print("path: " + str(request.path))
        print("path: " + str(request.path))

        if request.path.find("unread_notifications") != -1:
            print("shouldnt log because unread")
        else:
            print("path: " + str(request.path))
            if request.user.is_authenticated:
                print("user: " + str(request.user.id))
                print("rlc: " + str(request.user.rlc.id))
            print("date: " + str(timezone.now()))
            print("\n")

        # Code to be executed for each request/response after
        # the view is called.

        return response
