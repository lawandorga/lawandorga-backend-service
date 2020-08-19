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

from rest_framework import serializers
from backend.api.serializers import GroupNameSerializer
from backend.files.models import PermissionForFolder
from backend.files.serializers import (
    FolderPermissionSerializer,
    FolderNamePathSerializer,
)
from backend.api.errors import EntryAlreadyExistingError


class PermissionForFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionForFolder
        fields = "__all__"

    def validate(self, attrs):
        if PermissionForFolder.validate_values(attrs):
            return attrs
        raise serializers.ValidationError(
            "validation error at creating PermissionForFolder"
        )

    # def create(self, validated_data):
    #     if PermissionForFolder.already_existing(validated_data):
    #         raise EntryAlreadyExistingError("PermissionForFolder already exists")
    #     permission_for_folder = PermissionForFolder.objects.create(
    #         permission=validated_data.get('permission', None),
    #         rlc_has_permission=validated_data.get('rlc_has_permission', None),
    #         group_has_permission=validated_data.get('group_has_permission', None),
    #         user_has_permission=validated_data.get('user_has_permission', None),
    #         folder=validated_data.get('folder', None)
    #     )
    #     return permission_for_folder


class PermissionForFolderNestedSerializer(serializers.ModelSerializer):
    group_has_permission = GroupNameSerializer(many=False, read_only=True)
    permission = FolderPermissionSerializer(many=False, read_only=True)
    folder = FolderNamePathSerializer(many=False, read_only=True)

    class Meta:
        model = PermissionForFolder
        fields = "__all__"
