from rest_framework import serializers

from apps.api.serializers.user import UserProfileNameSerializer
from apps.recordmanagement.models.encrypted_record_message import \
    EncryptedRecordMessage


class EncryptedRecordMessageSerializer(serializers.ModelSerializer):
    message = serializers.CharField()

    class Meta:
        model = EncryptedRecordMessage
        fields = "__all__"

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["sender"] = self.context["request"].user
        return attrs


class EncryptedRecordMessageDetailSerializer(EncryptedRecordMessageSerializer):
    sender = UserProfileNameSerializer(read_only=True)

    class Meta:
        model = EncryptedRecordMessage
        fields = "__all__"
