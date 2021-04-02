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
from backend.recordmanagement.serializers import RecordTagNameSerializer
from backend.recordmanagement.models import EncryptedRecord
from backend.api.serializers import UserProfileNameSerializer
from rest_framework import serializers


class EncryptedRecordSerializer(serializers.ModelSerializer):
    note = serializers.CharField(allow_null=True, required=False, allow_blank=True)
    consultant_team = serializers.CharField(allow_null=True, required=False)
    lawyer = serializers.CharField(required=False)
    related_persons = serializers.CharField(allow_null=True, required=False)
    contact = serializers.CharField(allow_null=True, required=False)
    bamf_token = serializers.CharField(allow_null=True, required=False)
    foreign_token = serializers.CharField(allow_null=True, required=False)
    first_correspondence = serializers.CharField(allow_null=True, required=False)
    circumstances = serializers.CharField(allow_null=True, required=False)
    next_steps = serializers.CharField(allow_null=True, required=False)
    status_described = serializers.CharField(allow_null=True, required=False)
    additional_facts = serializers.CharField(allow_null=True, required=False)

    class Meta:
        model = EncryptedRecord
        fields = "__all__"


class EncryptedRecordListSerializer(EncryptedRecordSerializer):
    access = serializers.IntegerField()
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
