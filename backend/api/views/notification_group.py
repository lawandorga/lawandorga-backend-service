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

from typing import Any

from django.db.models import QuerySet, Q
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response

from backend.api.errors import CustomError
from backend.api.models import NotificationGroup
from backend.api.serializers import NotificationGroupOrderedSerializer
from backend.static.error_codes import (
    ERROR__API__ID_NOT_PROVIDED,
    ERROR__API__USER__NO_OWNERSHIP,
    ERROR__API__ID_NOT_FOUND,
    ERROR__API__PARAMS_NOT_VALID,
)


class NotificationGroupViewSet(viewsets.ModelViewSet):
    queryset = NotificationGroup.objects.all()
    serializer_class = NotificationGroupOrderedSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self) -> QuerySet:
        if not self.request.user.is_superuser:
            queryset = NotificationGroup.objects.filter(user=self.request.user)
        else:
            queryset = NotificationGroup.objects.all()

        request: Request = self.request
        if "filter" in request.query_params and request.query_params["filter"] != "":
            parts = request.query_params["filter"].split("___")
            queryset = queryset.filter(type__in=parts)

        if "sort" in request.query_params:
            if (
                "sortdirection" in request.query_params
                and request.query_params["sortdirection"] == "desc"
            ):
                to_sort = "-" + request.query_params["sort"]
            else:
                to_sort = request.query_params["sort"]
        else:
            to_sort = "-created"

        if to_sort != "created" and to_sort != "-last_activity":
            queryset = queryset.order_by(to_sort, "-last_activity")
        else:
            queryset = queryset.order_by(to_sort)

        return queryset

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if "pk" not in kwargs:
            raise CustomError(ERROR__API__ID_NOT_PROVIDED)

        try:
            notification_group: NotificationGroup = NotificationGroup.objects.get(
                pk=kwargs["pk"]
            )
        except Exception as e:
            raise CustomError(ERROR__API__ID_NOT_FOUND)

        if not request.user.is_superuser and request.user != notification_group.user:
            raise CustomError(ERROR__API__USER__NO_OWNERSHIP)

        if (
            "read" not in request.data
            or (request.data["read"] is not True and request.data["read"] is not False)
            or request.data.__len__() != 1
        ):
            raise CustomError(ERROR__API__PARAMS_NOT_VALID)

        notification_group.read = request.data["read"]
        notification_group.save()

        if request.data["read"]:
            for notification in notification_group.notifications.all():
                notification.read = True
                notification.save()

        return Response({"success": True})
