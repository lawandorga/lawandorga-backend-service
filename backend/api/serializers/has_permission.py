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

from rest_framework import serializers
from ..models import HasPermission
from ..errors import EntryAlreadyExistingError
from .permission import PermissionNameSerializer


class HasPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HasPermission
        fields = '__all__'

    """
    Validates if the values provided are correct and implement the model right
    """

    def validate(self, data):
        if HasPermission.validate_values(data):
            return data
        raise serializers.ValidationError("validationError at creating has_permission")

    def create(self, validated_data):
        if HasPermission.already_existing(validated_data):
            raise EntryAlreadyExistingError('entry already exists')
        has_permission = HasPermission.objects.create(
            permission=validated_data.get('permission', None),
            user_has_permission=validated_data.get('user_has_permission', None),
            group_has_permission=validated_data.get('group_has_permission', None),
            rlc_has_permission=validated_data.get('rlc_has_permission', None),
            permission_for_user=validated_data.get('permission_for_user', None),
            permission_for_group=validated_data.get('permission_for_group', None),
            permission_for_rlc=validated_data.get('permission_for_rlc', None)
        )
        return has_permission

    def update(self, instance, validated_data):
        has_permission, aa = HasPermission.objects.filter(permission=validated_data.get('permission', None))
        return instance


class HasPermissionOnlyPermissionForSerializer(serializers.ModelSerializer):
    permission = PermissionNameSerializer()

    class Meta:
        model = HasPermission
        fields = ('id', 'permission', 'permission_for_user', 'permission_for_group',)


class HasPermissionOnlyHasPermissionSerializer(serializers.ModelSerializer):
    permission = PermissionNameSerializer()

    class Meta:
        model = HasPermission
        fields = ('id', 'permission', 'user_has_permission', 'group_has_permission',)
