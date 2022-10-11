from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.core.records.models import RecordDeletion


class RecordDeletionSerializer(serializers.ModelSerializer):
    requested_by_detail = serializers.SerializerMethodField()
    processed_by_detail = serializers.SerializerMethodField()
    record_detail = serializers.SerializerMethodField()

    class Meta:
        model = RecordDeletion
        fields = "__all__"

    def validate(self, attrs):
        user = self.context["request"].user
        attrs = super().validate(attrs)
        if self.instance:
            if self.instance.state in ["gr", "de"]:
                raise ValidationError(
                    "This record deletion can not be updated, "
                    "because it is already granted or declined."
                )
            attrs["processed_by"] = user
            attrs["processed"] = timezone.now()
            if attrs["state"] not in ["gr", "de"]:
                raise ValidationError(
                    "You need to grant or decline this request. You can not just update it."
                )
        else:
            attrs["requested_by"] = user
            if "state" in attrs and attrs["state"] in ["gr", "de"]:
                raise ValidationError(
                    "A request can not have the state granted or declined on creation."
                )
        if attrs["record"].template.rlc != user.rlc:
            raise ValidationError(
                "You can only create or change deletion requests from your own LC."
            )
        return attrs

    def get_record_detail(self, obj):
        if obj.record and obj.record.identifier:
            return obj.record.identifier
        return "Deleted"

    def get_processed_by_detail(self, obj):
        if obj.processed_by:
            return obj.processed_by.name
        return ""

    def get_requested_by_detail(self, obj):
        return obj.requested_by.name
