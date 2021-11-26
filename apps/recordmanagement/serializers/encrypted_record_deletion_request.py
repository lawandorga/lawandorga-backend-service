from rest_framework.exceptions import ValidationError

from apps.recordmanagement.models.encrypted_record_deletion_request import EncryptedRecordDeletionRequest
from apps.recordmanagement.serializers import EncryptedRecordTokenSerializer
from apps.api.serializers.user import UserProfileNameSerializer
from rest_framework import serializers


class DeletionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncryptedRecordDeletionRequest
        fields = "__all__"


class DeletionRequestListSerializer(DeletionRequestSerializer):
    request_from = UserProfileNameSerializer(read_only=True)
    request_processed = UserProfileNameSerializer(read_only=True)
    record = EncryptedRecordTokenSerializer(read_only=True)


class DeletionRequestCreateSerializer(DeletionRequestSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not attrs['record'].user_has_permission(self.context['request'].user):
            raise ValidationError("You don't have the permission to delete this record.")
        return attrs
