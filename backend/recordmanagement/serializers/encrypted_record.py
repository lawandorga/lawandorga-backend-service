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
from backend.recordmanagement.models import EncryptedRecord
from backend.api.serializers.user import UserProfileNameSerializer
from .record_tag import RecordTagNameSerializer
from backend.static.encryption import AESEncryption
from backend.static.serializer_fields import EncryptedField


class EncryptedRecordFullDetailSerializer(serializers.ModelSerializer):
    tagged = RecordTagNameSerializer(many=True, read_only=True)
    working_on_record = UserProfileNameSerializer(many=True, read_only=True)
    e_record_messages = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    note = EncryptedField()
    consultant_team = EncryptedField()
    lawyer = EncryptedField()
    related_persons = EncryptedField()
    contact = EncryptedField()
    bamf_token = EncryptedField()
    foreign_token = EncryptedField()
    first_correspondence = EncryptedField()
    circumstances = EncryptedField()
    next_steps = EncryptedField()
    status_described = EncryptedField()
    additional_facts = EncryptedField()

    class Meta:
        model = EncryptedRecord
        fields = "__all__"
        extra_kwargs = {"creator": {"read_only": True}}

    def get_decrypted_data(self, records_aes_key):
        data = self.data
        AESEncryption.decrypt_field(data, data, "note", records_aes_key)
        AESEncryption.decrypt_field(data, data, "consultant_team", records_aes_key)
        AESEncryption.decrypt_field(data, data, "lawyer", records_aes_key)
        AESEncryption.decrypt_field(data, data, "related_persons", records_aes_key)
        AESEncryption.decrypt_field(data, data, "contact", records_aes_key)
        AESEncryption.decrypt_field(data, data, "bamf_token", records_aes_key)
        AESEncryption.decrypt_field(data, data, "foreign_token", records_aes_key)
        AESEncryption.decrypt_field(data, data, "first_correspondence", records_aes_key)
        AESEncryption.decrypt_field(data, data, "circumstances", records_aes_key)
        AESEncryption.decrypt_field(data, data, "next_steps", records_aes_key)
        AESEncryption.decrypt_field(data, data, "status_described", records_aes_key)
        AESEncryption.decrypt_field(data, data, "additional_facts", records_aes_key)
        return data


class EncryptedRecordNoDetailListSerializer(serializers.ListSerializer):
    def add_has_permission(self, user):
        data = []
        for record in self.instance.all():
            has_permission = record.user_has_permission(user)
            record_data = EncryptedRecordNoDetailSerializer(record).data
            record_data.update({"has_permission": has_permission})
            data.append(record_data)
        return data


class EncryptedRecordNoDetailSerializer(serializers.ModelSerializer):
    tagged = RecordTagNameSerializer(many=True, read_only=True)
    working_on_record = UserProfileNameSerializer(many=True, read_only=True)
    state = serializers.CharField()

    class Meta:
        list_serializer_class = EncryptedRecordNoDetailListSerializer
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
