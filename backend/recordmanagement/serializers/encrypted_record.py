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
        fields = '__all__'
        extra_kwargs = {
            'creator': {
                'read_only': True
            }
        }

    def get_decrypted_data(self, key):
        data = self.data
        data['note'] = AESEncryption.decrypt(data['note'], key)
        data['consultant_team'] = AESEncryption.decrypt(data['consultant_team'], key)
        data['lawyer'] = AESEncryption.decrypt(data['lawyer'], key)
        data['related_persons'] = AESEncryption.decrypt(data['related_persons'], key)
        data['contact'] = AESEncryption.decrypt(data['contact'], key)
        data['bamf_token'] = AESEncryption.decrypt(data['bamf_token'], key)
        data['foreign_token'] = AESEncryption.decrypt(data['foreign_token'], key)
        data['first_correspondence'] = AESEncryption.decrypt(data['first_correspondence'], key)
        data['circumstances'] = AESEncryption.decrypt(data['circumstances'], key)
        data['next_steps'] = AESEncryption.decrypt(data['next_steps'], key)
        data['status_described'] = AESEncryption.decrypt(data['status_described'], key)
        data['additional_facts'] = AESEncryption.decrypt(data['additional_facts'], key)
        return data


class EncryptedRecordNoDetailSerializer(serializers.ModelSerializer):
    tagged = RecordTagNameSerializer(many=True, read_only=True)
    working_on_record = UserProfileNameSerializer(many=True, read_only=True)
    state = serializers.CharField()

    class Meta:
        model = EncryptedRecord
        fields = ('id', 'last_contact_date', 'state', 'official_note',
                  'record_token', 'working_on_record', 'tagged')


class EncryptedRecordTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncryptedRecord
        fields = ('id', 'record_token')

