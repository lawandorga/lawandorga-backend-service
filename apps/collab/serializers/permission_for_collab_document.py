#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2021  Dominik Walser
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

from apps.api.serializers import GroupSerializer
from apps.collab.models import PermissionForCollabDocument
from apps.collab.serializers import CollabDocumentSerializer


class PermissionForCollabDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionForCollabDocument
        fields = "__all__"


class PermissionForCollabDocumentNestedSerializer(serializers.ModelSerializer):
    group_has_permission = GroupSerializer(many=False, read_only=True)
    document = CollabDocumentSerializer(many=False, read_only=True)

    class Meta:
        model = PermissionForCollabDocument
        fields = "__all__"
