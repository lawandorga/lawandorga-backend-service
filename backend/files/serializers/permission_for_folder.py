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
from backend.api.serializers import GroupSerializer, GroupNameSerializer
from backend.files.models.permission_for_folder import PermissionForFolder
from backend.files.serializers import (
    FolderPermissionSerializer,
    FolderNamePathSerializer, FolderSimpleSerializer,
)
from backend.api.errors import EntryAlreadyExistingError


class PermissionForFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionForFolder
        fields = "__all__"


class PermissionForFolderNestedSerializer(serializers.ModelSerializer):
    group_has_permission = GroupNameSerializer(many=False, read_only=True)
    permission = FolderPermissionSerializer(many=False, read_only=True)
    folder = FolderSimpleSerializer(many=False, read_only=True)
    type = serializers.SerializerMethodField('get_type')
    source = serializers.SerializerMethodField('get_source')

    class Meta:
        model = PermissionForFolder
        fields = "__all__"

    def __init__(self, instance=None, from_direction='', *args, **kwargs):
        super().__init__(instance, *args, **kwargs)
        self.from_direction = from_direction

    def get_source(self, obj):
        if self.from_direction == 'BELOW':
            return 'BELOW'
        elif self.from_direction == 'ABOVE':
            return 'ABOVE'
        return 'NORMAL'

    def get_type(self, obj):
        if self.from_direction in ['BELOW', 'ABOVE']:
            return 'See'
        return obj.permission.name
