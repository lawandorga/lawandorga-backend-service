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
from rest_framework.exceptions import ValidationError

from backend.api.serializers import UserProfileNameSerializer
from backend.files.models import Folder
from backend.files.models.file import File


class AddUserMixin:
    def validate(self, attrs):
        attrs = super().validate(attrs)
        if 'creator' not in attrs:
            attrs['creator'] = self.context['request'].user
        return attrs


class FileSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField('get_type')

    class Meta:
        model = File
        fields = "__all__"

    def get_type(self, obj):
        return 'FILE'


class FileCreateSerializer(AddUserMixin, FileSerializer):
    name = serializers.CharField(required=False)
    folder = serializers.PrimaryKeyRelatedField(required=False, queryset=Folder.objects.all())

    class Meta:
        model = File
        fields = ['folder', 'name', 'type', 'key', 'created', 'id']

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if 'file' not in self.context['request'].FILES:
            raise ValidationError("A file is required to be submitted with the name 'file'.")
        attrs['name'] = self.context['request'].FILES['file'].name
        if 'folder' not in attrs:
            attrs['folder'] = Folder.objects.get(parent=None, rlc=self.context['request'].user.rlc)
        return attrs

    def validate_folder(self, folder):
        if folder.rlc != self.context['request'].user.rlc:
            raise ValidationError('The folder needs to be in your RLC.')
        return folder
