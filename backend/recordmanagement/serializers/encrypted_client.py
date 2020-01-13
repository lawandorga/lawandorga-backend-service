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
from backend.recordmanagement.models import EncryptedClient
from backend.static.serializer_fields import EncryptedField
from backend.static.encryption import AESEncryption


class EncryptedClientListSerializer(serializers.ListSerializer):
    def get_decrypted_data(self, rlcs_private_key):
        data = []
        for client in self.instance.all():
            client_password = client.get_password(rlcs_private_key)
            client_data = EncryptedClientSerializer(client).get_decrypted_data(client_password)
            data.append(client_data)
        return data


class EncryptedClientSerializer(serializers.ModelSerializer):
    e_records = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    name = EncryptedField()
    note = EncryptedField()
    phone_number = EncryptedField()

    class Meta:
        list_serializer_class = EncryptedClientListSerializer
        model = EncryptedClient
        exclude = ['encrypted_client_key']

    def get_decrypted_data(self, client_key):
        data = self.data
        AESEncryption.decrypt_field(data, data, 'name', client_key)
        AESEncryption.decrypt_field(data, data, 'note', client_key)
        AESEncryption.decrypt_field(data, data, 'phone_number', client_key)
        return data


class EncryptedClientNameSerializer(serializers.ModelSerializer):
    name = EncryptedField()

    # TODO: ! encryption when is this used??
    class Meta:
        model = EncryptedClient
        fields = ('id', 'name', 'origin_country', )
