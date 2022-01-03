from apps.recordmanagement.models.deletion import RecordDeletion
from apps.recordmanagement.serializers import EncryptedRecordTokenSerializer
from apps.api.serializers.user import UserProfileNameSerializer
from rest_framework.exceptions import ValidationError
from rest_framework import serializers


class RecordDeletionSerializer(serializers.ModelSerializer):
    requested_by_detail = serializers.SerializerMethodField()
    processed_by_detail = serializers.SerializerMethodField()
    record_detail = serializers.SerializerMethodField()

    class Meta:
        model = RecordDeletion
        fields = "__all__"

    def get_record_detail(self, obj):
        if obj.record and obj.record.identifier:
            return obj.record.identifier
        return 'Deleted'

    def get_processed_by_detail(self, obj):
        if obj.processed_by:
            return obj.processed_by.name
        return ''

    def get_requested_by_detail(self, obj):
        return obj.requested_by.name


class DeletionRequestListSerializer(RecordDeletionSerializer):
    request_from = UserProfileNameSerializer(read_only=True)
    request_processed = UserProfileNameSerializer(read_only=True)
    record = EncryptedRecordTokenSerializer(read_only=True)


class DeletionRequestCreateSerializer(RecordDeletionSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not attrs['record'].user_has_permission(self.context['request'].user):
            raise ValidationError("You don't have the permission to delete this record.")
        return attrs
