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
from backend.api.serializers import UserProfileNameSerializer
from backend.recordmanagement.models import EncryptedRecordDocumentDeletionRequest
from backend.recordmanagement.serializers import (
    EncryptedRecordDocumentSerializer,
    EncryptedRecordDocumentNameSerializer,
    EncryptedRecordTokenSerializer,
)


class EncryptedRecordDocumentDeletionRequestSerializer(serializers.ModelSerializer):
    request_from = UserProfileNameSerializer(many=False, read_only=True)
    request_processed = UserProfileNameSerializer(many=False, read_only=True)
    document = EncryptedRecordDocumentSerializer(
        many=False, read_only=True, allow_null=True
    )

    class Meta:
        model = EncryptedRecordDocumentDeletionRequest
        fields = "__all__"


class EncryptedRecordDocumentDeletionRequestListSerializer(serializers.ModelSerializer):
    request_from = UserProfileNameSerializer(many=False, read_only=True)
    request_processed = UserProfileNameSerializer(many=False, read_only=True)
    record = EncryptedRecordTokenSerializer(many=False, read_only=True)

    document = EncryptedRecordDocumentNameSerializer(
        many=False, read_only=True, allow_null=True
    )

    class Meta:
        model = EncryptedRecordDocumentDeletionRequest
        fields = "__all__"
