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
from backend.api.serializers import RlcSimpleSerializer
from backend.api.models.rlc import Rlc
from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework import mixins
from django.conf import settings


class RlcViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Rlc.objects.all()
    serializer_class = RlcSimpleSerializer
    permission_classes = []
    authentication_classes = []

    def get_queryset(self) -> QuerySet:
        queryset = Rlc.objects.all().order_by("name")
        return queryset
