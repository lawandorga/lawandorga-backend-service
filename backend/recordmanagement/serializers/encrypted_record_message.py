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
from backend.recordmanagement.models import EncryptedRecordMessage
from backend.api.serializers.user import UserProfileNameSerializer
from backend.static.serializer_fields import EncryptedField
from backend.static.encryption import AESEncryption


class EncryptedRecordMessageListSerializer(serializers.ListSerializer):
    def get_decrypted_data(self, record_aes_key):
        data = []
        for message in self.instance.all():
            data.append(
                EncryptedRecordMessageSerializer(message).get_decrypted_data(
                    record_aes_key
                )
            )
        return data


class EncryptedRecordMessageSerializer(serializers.ModelSerializer):
    sender = UserProfileNameSerializer(many=False, read_only=True)
    message = EncryptedField()

    class Meta:
        list_serializer_class = EncryptedRecordMessageListSerializer
        model = EncryptedRecordMessage
        fields = "__all__"

    def get_decrypted_data(self, key):
        data = self.data
        AESEncryption.decrypt_field(data, data, "message", key)
        return data
