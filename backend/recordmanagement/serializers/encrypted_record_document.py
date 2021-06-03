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

from backend.recordmanagement.models.encrypted_record_document import (
    EncryptedRecordDocument,
)
from backend.recordmanagement.serializers import RecordDocumentTagSerializer


class RecordDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncryptedRecordDocument
        fields = '__all__'


class RecordDocumentCreateSerializer(RecordDocumentSerializer):
    name = serializers.CharField(required=False)

    class Meta:
        model = EncryptedRecordDocument
        fields = ['id', 'name', 'record', 'creator', 'created_on']

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if 'file' not in self.context['request'].FILES:
            raise ValidationError("A file is required to be submitted with the name 'file'.")
        attrs['name'] = self.context['request'].FILES['file'].name
        return attrs


class OldEncryptedRecordDocumentSerializer(serializers.ModelSerializer):
    tagged = RecordDocumentTagSerializer(many=True, read_only=True)

    class Meta:
        model = EncryptedRecordDocument
        fields = "__all__"


class EncryptedRecordDocumentNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncryptedRecordDocument
        fields = (
            "name",
            "id",
        )
