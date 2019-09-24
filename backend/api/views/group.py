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
from backend.static import error_codes
from backend.static import permissions
from .. import models, serializers


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.GroupSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_superuser:
            # return models.Group.objects.get_groups_with_mange_rights(user)
            return models.Group.objects.get_visible_groups_for_user(user)
            # if user.has_permission(permissions.PERMISSION_MANAGE_GROUPS_RLC, for_rlc=user.rlc):
            #     return models.Group.objects.filter(from_rlc=user.rlc)
            # else:
            #     return models.Group.objects.filter(from_rlc=user.rlc, visible=True)
        else:
            return models.Group.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.GroupNameSerializer
        else:
            return serializers.GroupSerializer

    def perform_create(self, serializer):
        creator = models.UserProfile.objects.get(id=self.request.user.id)
        serializer.save(creator=creator)

    def create(self, request, *args, **kwargs):
        if not request.user.has_permission(
            permissions.PERMISSION_MANAGE_GROUPS_RLC, for_rlc=request.user.rlc) and not request.user.has_permission(
            permissions.PERMISSION_ADD_GROUP_RLC, for_rlc=request.user.rlc):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        if 'name' not in request.data or 'visible' not in request.data:
            raise CustomError(error_codes.ERROR__API__GROUP__CAN_NOT_CREATE)

        group = models.Group(name=request.data['name'], visible=request.data['visible'], creator=request.user,
                             from_rlc=request.user.rlc)
        group.save()
        return Response(serializers.GroupNameSerializer(group).data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = serializers.GroupShowSerializer(instance)
        return Response(serializer.data)


class GroupMemberViewSet(APIView):
    def post(self, request):
        if 'action' not in request.data or 'group_id' not in request.data or 'user_id' not in request.data:
            raise CustomError(error_codes.ERROR__API__MISSING_ARGUMENT)
        try:
            group = models.Group.objects.get(pk=request.data['group_id'])
        except:
            raise CustomError(error_codes.ERROR__API__GROUP__GROUP_NOT_FOUND)

        try:
            user = models.UserProfile.objects.get(pk=request.data['user_id'])
        except:
            raise CustomError(error_codes.ERROR__API__USER__NOT_FOUND)

        if request.data['action'] == 'add':
            group.group_members.add(user)
            group.save()
            return Response(serializers.GroupSerializer(group).data)
        elif request.data['action'] == 'remove':
            group.group_members.remove(user)
            group.save()
            return Response(serializers.GroupSerializer(group).data)

        raise CustomError(error_codes.ERROR__API__NO_ACTION_PROVIDED)
