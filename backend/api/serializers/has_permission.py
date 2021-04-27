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

from rest_framework import serializers
from ..errors import EntryAlreadyExistingError
from ..models.has_permission import HasPermission


class HasPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HasPermission
        fields = "__all__"

    def validate(self, data):
        if HasPermission.validate_values(data):
            return data
        raise serializers.ValidationError("validationError at creating has_permission")

    def create(self, validated_data):
        if HasPermission.already_existing(validated_data):
            raise EntryAlreadyExistingError("entry already exists")
        return super().create(validated_data)


class HasPermissionNameSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(method_name='get_name')

    class Meta:
        model = HasPermission
        fields = '__all__'

    def get_name(self, obj):
        return obj.permission.name
