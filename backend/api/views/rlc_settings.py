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

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.api.errors import CustomError
from backend.static.error_codes import (
    ERROR__API__PERMISSION__INSUFFICIENT,
    ERROR__API__RLC_SETTINGS__WRONG_COUNT,
)
from backend.api.models import RlcSettings
from backend.api.serializers import RlcSettingsSerializer


class RlcSettingsViewSet(viewsets.ModelViewSet):
    queryset = RlcSettings.objects.all()
    serializer_class = RlcSettingsSerializer

    def create(self, request):
        raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)

    def update(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)

        return super().update(request, args, kwargs)


class RlcSettingsMineViewSet(APIView):
    def get(self, request):
        settings = RlcSettings.objects.filter(rlc=request.user.rlc)
        if settings.count() != 1:
            raise CustomError(ERROR__API__RLC_SETTINGS__WRONG_COUNT)
        data = RlcSettingsSerializer(settings.first()).data
        return Response(data)
