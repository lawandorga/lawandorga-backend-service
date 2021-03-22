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

from backend.collab.models import TextDocument
from backend.static.encryption import AESEncryption
from backend.static.serializer_fields import EncryptedField

from backend.api.serializers import UserProfileNameSerializer


class TextDocumentSerializer(serializers.ModelSerializer):
    creator = UserProfileNameSerializer(many=False, read_only=True)
    last_editor = UserProfileNameSerializer(many=False, read_only=True)
    # content = EncryptedField()

    class Meta:
        model = TextDocument
        fields = "__all__"

    # def get_decrypted_data(self, aes_key: str) -> {}:
    #     data = self.data
    #     AESEncryption.decrypt_field(data, data, "content", aes_key)
    #     return data


# class TextDocumentNameSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TextDocument
#         fields = ("pk", "]") # TODO: change this
