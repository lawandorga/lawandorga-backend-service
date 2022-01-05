from rest_framework import serializers
from apps.api.serializers.user import UserProfileNameSerializer
from apps.recordmanagement.models.encrypted_record_permission import EncryptedRecordPermission


class EncryptedRecordPermissionSerializer(serializers.ModelSerializer):
    request_from = UserProfileNameSerializer(many=False, read_only=True)
    request_processed = UserProfileNameSerializer(many=False, read_only=True)

    class Meta:
        model = EncryptedRecordPermission
        fields = "__all__"
