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
from rest_framework.exceptions import ValidationError

from backend.recordmanagement.serializers import RecordTagNameSerializer, RecordEncryptionSerializer, TagSerializer
from backend.recordmanagement.models import EncryptedRecord, RecordEncryption
from backend.api.serializers import UserProfileNameSerializer
from rest_framework import serializers


class EncryptedRecordSerializer(serializers.ModelSerializer):
    note = serializers.CharField(allow_blank=True, required=False)
    consultant_team = serializers.CharField(allow_blank=True, required=False)
    lawyer = serializers.CharField(allow_blank=True, required=False)
    related_persons = serializers.CharField(allow_blank=True, required=False)
    contact = serializers.CharField(allow_blank=True, required=False)
    bamf_token = serializers.CharField(allow_blank=True, required=False)
    foreign_token = serializers.CharField(allow_blank=True, required=False)
    first_correspondence = serializers.CharField(allow_blank=True, required=False)
    circumstances = serializers.CharField(allow_blank=True, required=False)
    next_steps = serializers.CharField(allow_blank=True, required=False)
    status_described = serializers.CharField(allow_blank=True, required=False)
    additional_facts = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = EncryptedRecord
        fields = "__all__"

    def validate(self, attrs):
        token = attrs['record_token']
        if 'from_rlc' in attrs and EncryptedRecord.objects.filter(record_token=token,
                                                                  from_rlc=attrs['from_rlc']).exists():
            raise ValidationError('The record token is already used. Please choose another record token.')
        return attrs


class EncryptedRecordListSerializer(EncryptedRecordSerializer):
    access = serializers.SerializerMethodField('get_access')
    tagged = RecordTagNameSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    working_on_record = UserProfileNameSerializer(many=True, read_only=True)

    class Meta:
        model = EncryptedRecord
        fields = [
            "id",
            "state",
            "official_note",
            "record_token",
            "working_on_record",
            "tagged",
            'tags',
            "access",
            "created_on",
            "last_edited"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = self.context['request'].user

    def get_access(self, obj):
        return obj.encryptions.filter(user=self.user).exists()


class EncryptedRecordDetailSerializer(EncryptedRecordSerializer):
    tagged = RecordTagNameSerializer(many=True, read_only=True)
    working_on_record = UserProfileNameSerializer(many=True, read_only=True)


class EncryptedRecordTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncryptedRecord
        fields = ("id", "record_token")
