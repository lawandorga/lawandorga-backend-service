from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.core.records.models.encrypted_record_document import EncryptedRecordDocument


class RecordDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncryptedRecordDocument
        fields = "__all__"


class RecordDocumentCreateSerializer(RecordDocumentSerializer):
    name = serializers.CharField(required=False)

    class Meta:
        model = EncryptedRecordDocument
        fields = ["id", "name", "record", "created_on"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if "file" not in self.context["request"].FILES:
            raise ValidationError(
                {"file": "There seems to be no file. Please choose a file."}
            )
        attrs["name"] = self.context["request"].FILES["file"].name
        return attrs
