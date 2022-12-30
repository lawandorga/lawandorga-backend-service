from rest_framework import serializers

from core.auth.models import RlcUser
from core.messages.models import EncryptedRecordMessage


class EncryptedRecordMessageSerializer(serializers.ModelSerializer):
    message = serializers.CharField()

    class Meta:
        model = EncryptedRecordMessage
        fields = "__all__"

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["sender"] = self.context["request"].user.rlc_user
        return attrs


class MessageSenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = RlcUser
        fields = ("name", "email")


class EncryptedRecordMessageDetailSerializer(EncryptedRecordMessageSerializer):
    sender = MessageSenderSerializer(read_only=True)

    class Meta:
        model = EncryptedRecordMessage
        fields = "__all__"
