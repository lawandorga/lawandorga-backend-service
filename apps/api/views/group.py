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
from rest_framework.exceptions import PermissionDenied

from apps.recordmanagement.models import (
    EncryptedRecord,
    RecordEncryption,
    Notification,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.api.serializers import (
    GroupSerializer,
    GroupMembersSerializer,
    GroupAddMemberSerializer, UserProfileSerializer, OldHasPermissionSerializer, HasPermissionNameSerializer,
)
from rest_framework.request import Request
from apps.api.errors import CustomError
from apps.api.models import Group, UserProfile, RlcUser
from apps.static import error_codes, permissions
from rest_framework import viewsets, status


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer

    def get_queryset(self):
        return Group.objects.get_visible_groups_for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        # permission stuff
        if not request.user.has_permission(permissions.PERMISSION_MANAGE_GROUPS_RLC):
            raise PermissionDenied()

        # add data
        request.data["creator"] = request.user.pk
        request.data["from_rlc"] = request.user.rlc.pk

        # do the usual stuff
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = GroupMembersSerializer
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request: Request, *args, **kwargs):
        # permission stuff
        if not request.user.has_permission(permissions.PERMISSION_MANAGE_GROUPS_RLC):
            raise PermissionDenied()

        # do the usual stuff
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def members(self, *args, **kwargs):
        group = self.get_object()
        members = group.group_members.all()
        return Response(UserProfileSerializer(members, many=True).data)

    @action(detail=True, methods=['get'])
    def permissions(self, *args, **kwargs):
        group = self.get_object()
        permissions = group.group_has_permission.all()
        return Response(HasPermissionNameSerializer(permissions, many=True).data)

    @action(detail=True, methods=['post'])
    def remove(self, request, pk=None, *arsg, **kwargs):
        if not request.user.has_permission(permissions.PERMISSION_MANAGE_GROUPS_RLC):
            raise PermissionDenied()

        # get the group
        group = self.get_object()

        # get the data
        serializer = GroupAddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        member = UserProfile.objects.get(pk=serializer.validated_data["member"])

        # remove the member
        group.group_members.remove(member)
        Notification.objects.notify_group_member_removed(
            request.user, member, group
        )

        return Response(status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post", "delete"])
    def member(self, request: Request, pk=None):
        # permission stuff
        if not request.user.has_permission(permissions.PERMISSION_MANAGE_GROUPS_RLC):
            raise PermissionDenied()

        # get the group
        group = self.get_object()

        # get the data
        serializer = GroupAddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        member = RlcUser.objects.get(pk=serializer.validated_data["member"]).user

        # add member to group
        if request.method == "POST":
            group.group_members.add(member)
            # check if group can see encrypted data and add keys for the new member if so
            if group.group_has_record_encryption_keys_permission():
                private_key_user = request.user.get_private_key(request=request)
                records = list(
                    EncryptedRecord.objects.filter(from_rlc=request.user.rlc)
                )
                for record in records:
                    if not RecordEncryption.objects.filter(user=member, record=record).exists():
                        try:
                            record_key = record.get_decryption_key(
                                request.user, private_key_user
                            )
                        except Exception:
                            continue
                        public_key_member = member.get_public_key()
                        record_encryption = RecordEncryption(
                            user=member, record=record, encrypted_key=record_key
                        )
                        record_encryption.encrypt(public_key_member)
                        record_encryption.save()
            # notify
            Notification.objects.notify_group_member_added(request.user, member, group)

            # return the added user
            return Response(UserProfileSerializer(member).data, status=status.HTTP_200_OK)

        # remove member from group
        if request.method == "DELETE":
            group.group_members.remove(member)
            Notification.objects.notify_group_member_removed(
                request.user, member, group
            )

        # return something
        return Response(status.HTTP_204_NO_CONTENT)
