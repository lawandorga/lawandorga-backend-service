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
from backend.api.models.notification import Notification
from backend.static.error_codes import ERROR__API__ID_NOT_PROVIDED, ERROR__API__NOTIFICATION__UPDATE_INVALID, \
    ERROR__API__USER__NO_OWNERSHIP, ERROR__API__ID_NOT_FOUND
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import action
from backend.api.serializers import NotificationSerializer
from rest_framework.response import Response
from rest_framework.request import Request
from backend.api.models import NotificationGroup
from backend.api.errors import CustomError
from django.db.models import QuerySet
from rest_framework import viewsets
from typing import Any


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self) -> QuerySet:
        if not self.request.user.is_superuser:
            queryset = Notification.objects.filter(user=self.request.user)
        else:
            queryset = Notification.objects.all()
        request: Request = self.request
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

        if to_sort != "created" and to_sort != "-created":
            queryset = queryset.order_by(to_sort, "-created")
        else:
            queryset = queryset.order_by(to_sort)

        return queryset

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if "pk" not in kwargs:
            raise CustomError(ERROR__API__ID_NOT_PROVIDED)
        try:
            notification: Notification = Notification.objects.get(pk=kwargs["pk"])
        except Exception as e:
            raise CustomError(ERROR__API__ID_NOT_FOUND)

        if request.user != notification.notification_group.user:
            raise CustomError(ERROR__API__USER__NO_OWNERSHIP)

        if "read" not in request.data or request.data.__len__() > 1:
            raise CustomError(ERROR__API__NOTIFICATION__UPDATE_INVALID)
        notification.read = request.data["read"]
        notification.save()

        return Response({"success": True})

    @action(detail=False, methods=['get'])
    def unread(self, request: Request):
        unread = NotificationGroup.objects.filter(user=request.user, read=False).count()
        return Response({'unread_notification': unread})
