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
from backend.static.error_codes import ERROR__API__EMAIL__NO_EMAIL_PROVIDED
from rest_framework.response import Response
from backend.static.emails import EmailSender
from rest_framework.views import APIView
from backend.api.errors import CustomError
from ..models.rlc import Rlc
from django.conf import settings
import json


class SendEmailViewSet(APIView):
    def post(self, request):
        if "email" in request.data:
            email = request.data["email"]
        else:
            raise CustomError(ERROR__API__EMAIL__NO_EMAIL_PROVIDED)
        EmailSender.test_send(email)
        return Response()


class GetRlcsViewSet(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        rlcs = Rlc.objects.all().order_by("name")
        if settings.PROD:
            rlcs = rlcs.exclude(name="Dummy RLC")
        data = json.dumps([rlc.name for rlc in rlcs])
        return Response(data)
