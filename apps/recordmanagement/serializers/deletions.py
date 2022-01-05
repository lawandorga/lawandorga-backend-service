from apps.recordmanagement.models.deletion import RecordDeletion
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
