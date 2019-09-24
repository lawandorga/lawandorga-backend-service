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

from ..models import Group
from ..serializers.user import UserProfileNameSerializer


class GroupSerializer(serializers.ModelSerializer):
    group_has_permission = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, required=False
    )
    permission_for_group = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, required=False,
    )
    group_members = UserProfileNameSerializer(many=True)

    class Meta:
        model = Group
        fields = '__all__'


class GroupSmallSerializer(serializers.ModelSerializer):
    group_has_permission = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True
    )
    permission_for_group = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True
    )

    class Meta:
        model = Group
        fields = ('id', 'name', 'group_has_permission', 'permission_for_group', )


class GroupNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


class GroupShowSerializer(serializers.ModelSerializer):
    group_members = UserProfileNameSerializer(many=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'group_members', 'description', 'note', 'visible', 'note')
