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

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.api import models, serializers
from backend.api.errors import CustomError
from backend.recordmanagement.helpers import add_record_encryption_keys_for_users
from backend.static import error_codes, permissions
from backend.static.middleware import get_private_key_from_request


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.GroupSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_superuser:
            return models.Group.objects.get_visible_groups_for_user(user)
        else:
            return models.Group.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.GroupNameSerializer
        else:
            return serializers.GroupSerializer

    def perform_create(self, serializer):
        creator = models.UserProfile.objects.get(id=self.request.user.id)
        serializer.save(creator=creator)

    def create(self, request, *args, **kwargs):
        user: models.UserProfile = request.user
        if not user.has_permission(
            permissions.PERMISSION_MANAGE_GROUPS_RLC, for_rlc=request.user.rlc
        ) and not user.has_permission(
            permissions.PERMISSION_ADD_GROUP_RLC, for_rlc=request.user.rlc
        ):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        if "name" not in request.data or "visible" not in request.data:
            raise CustomError(error_codes.ERROR__API__GROUP__CAN_NOT_CREATE)

        if models.Group.objects.filter(
            name=request.data["name"], from_rlc=user.rlc
        ).exists():
            raise CustomError(error_codes.ERROR__API__GROUP__ALREADY_EXISTING)

        group = models.Group(
            name=request.data["name"],
            visible=request.data["visible"],
            creator=user,
            from_rlc=user.rlc,
        )
        group.save()
        return Response(serializers.GroupNameSerializer(group).data, status=201)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = serializers.GroupShowSerializer(instance)
        return Response(serializer.data)


class GroupMembersViewSet(APIView):
    def post(self, request):
        request_user: models.UserProfile = request.user
        if not request_user.has_permission(
            permissions.PERMISSION_MANAGE_GROUPS_RLC, for_rlc=request_user.rlc
        ):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        if (
            "action" not in request.data
            or "group_id" not in request.data
            or "user_ids" not in request.data
        ):
            raise CustomError(error_codes.ERROR__API__MISSING_ARGUMENT)
        try:
            group = models.Group.objects.get(pk=request.data["group_id"])
        except:
            raise CustomError(error_codes.ERROR__API__GROUP__GROUP_NOT_FOUND)

        users = []
        for user_id in request.data["user_ids"]:
            try:
                user = models.UserProfile.objects.get(pk=user_id)
                users.append(user)
            except:
                raise CustomError(error_codes.ERROR__API__USER__NOT_FOUND)

        if request.data["action"] == "add":
            if group.group_has_record_encryption_keys_permission():
                granting_users_private_key = get_private_key_from_request(request)
                add_record_encryption_keys_for_users(
                    request.user, granting_users_private_key, users
                )
            for user in users:
                group.group_members.add(user)
                models.Notification.objects.notify_group_member_added(
                    request.user, user, group
                )
            group.save()
            return Response(serializers.GroupSerializer(group).data)
        elif request.data["action"] == "remove":
            for user in users:
                group.group_members.remove(user)
                models.Notification.objects.notify_group_member_removed(
                    request.user, user, group
                )

            group.save()
            return Response(serializers.GroupSerializer(group).data)

        raise CustomError(error_codes.ERROR__API__NO_ACTION_PROVIDED)
