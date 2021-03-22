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
from backend.recordmanagement.helpers import add_record_encryption_keys_for_users
from backend.recordmanagement.models import EncryptedRecord, RecordEncryption, Notification
from backend.static.middleware import get_private_key_from_request
from rest_framework.decorators import action
from rest_framework.response import Response
from backend.api.serializers import GroupSerializer, GroupMembersSerializer, GroupAddMemberSerializer
from rest_framework.request import Request
from rest_framework.views import APIView
from backend.api.errors import CustomError
from backend.api.models import Group, UserProfile
from backend.static import error_codes, permissions
from rest_framework import viewsets
from backend.api import models, serializers


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer

    def get_queryset(self):
        return Group.objects.get_visible_groups_for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        # permission stuff
        if not request.user.has_permission(
            permissions.PERMISSION_MANAGE_GROUPS_RLC, for_rlc=request.user.rlc
        ) and not request.user.has_permission(
            permissions.PERMISSION_ADD_GROUP_RLC, for_rlc=request.user.rlc
        ):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        # add data
        request.data['creator'] = request.user
        request.data['from_rlc'] = request.user.rlc

        # do the usual stuff
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = GroupMembersSerializer
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post', 'delete'])
    def member(self, request: Request, pk=None):
        # permission stuff
        if not request.user.has_permission(permissions.PERMISSION_MANAGE_GROUPS_RLC, for_rlc=request.user.rlc):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        # get the group
        group = self.get_object()

        # get the data
        serializer = GroupAddMemberSerializer(request.data)
        member = UserProfile.objects.get(pk=serializer.validated_data['member'])

        # add member to group
        if request.method == 'POST':
            group.group_members.add(member)
            # check if group can see encrypted data and add keys for the new member if so
            if group.group_has_record_encryption_keys_permission():
                private_key_user = request.user.get_private_key(request=request)
                records = list(EncryptedRecord.objects.filter(from_rlc=request.user.rlc))
                for record in records:
                    record_key = record.get_decryption_key(request.user, private_key_user)
                    public_key_member = member.get_public_key()
                    record_encryption = RecordEncryption(
                        user=member,
                        record=record,
                        record_key=record_key
                    )
                    record_encryption.encrypt(public_key_member)
                    record_encryption.save()
            # notify
            Notification.objects.notify_group_member_added(request.user, member, group)

        # remove member from group
        if request.method == 'DELETE':
            group.group_members.remove(member)
            Notification.objects.notify_group_member_removed(request.user, member, group)

        # return something
        return Response(self.get_serializer(group).data)


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
