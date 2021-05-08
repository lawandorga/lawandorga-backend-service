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
from backend.recordmanagement.serializers import RecordTagNameSerializer, RecordEncryptionSerializer
from backend.recordmanagement.models import EncryptedRecord, RecordEncryption
from backend.api.serializers import UserProfileNameSerializer
from rest_framework import serializers


class EncryptedRecordSerializer(serializers.ModelSerializer):
    note = serializers.CharField(allow_blank=True)
    consultant_team = serializers.CharField(allow_blank=True)
    lawyer = serializers.CharField(allow_blank=True)
    related_persons = serializers.CharField(allow_blank=True)
    contact = serializers.CharField(allow_blank=True)
    bamf_token = serializers.CharField(allow_blank=True)
    foreign_token = serializers.CharField(allow_blank=True)
    first_correspondence = serializers.CharField(allow_blank=True)
    circumstances = serializers.CharField(allow_blank=True)
    next_steps = serializers.CharField(allow_blank=True)
    status_described = serializers.CharField(allow_blank=True)
    additional_facts = serializers.CharField(allow_blank=True)

    class Meta:
        model = EncryptedRecord
        fields = "__all__"


class EncryptedRecordListSerializer(EncryptedRecordSerializer):
    access = serializers.SerializerMethodField('get_access')
    tagged = RecordTagNameSerializer(many=True, read_only=True)
    working_on_record = UserProfileNameSerializer(many=True, read_only=True)

    class Meta:
        model = EncryptedRecord
        fields = [
            "id",
            "last_contact_date",
            "state",
            "official_note",
            "record_token",
            "working_on_record",
            "tagged",
            "access",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = self.context['request'].user

    def get_access(self, obj):
        return obj.encryptions.filter(user=self.user).exists()


class EncryptedRecordDetailSerializer(EncryptedRecordSerializer):
    tagged = RecordTagNameSerializer(many=True, read_only=True)
    working_on_record = UserProfileNameSerializer(many=True, read_only=True)


class EncryptedRecordNoDetailSerializer(serializers.ModelSerializer):
    tagged = RecordTagNameSerializer(many=True, read_only=True)
    working_on_record = UserProfileNameSerializer(many=True, read_only=True)
    state = serializers.CharField()

    class Meta:
        model = EncryptedRecord
        fields = (
            "id",
            "last_contact_date",
            "state",
            "official_note",
            "record_token",
            "working_on_record",
            "tagged",
        )


class EncryptedRecordTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncryptedRecord
        fields = ("id", "record_token")
