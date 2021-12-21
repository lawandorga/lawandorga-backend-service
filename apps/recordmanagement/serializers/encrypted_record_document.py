from apps.recordmanagement.models.encrypted_record_document import EncryptedRecordDocument
from rest_framework.exceptions import ValidationError
from rest_framework import serializers


class RecordDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncryptedRecordDocument
        fields = '__all__'


class RecordDocumentCreateSerializer(RecordDocumentSerializer):
    name = serializers.CharField(required=False)

    class Meta:
        model = EncryptedRecordDocument
        fields = ['id', 'name', 'record', 'creator', 'created_on']

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if 'file' not in self.context['request'].FILES:
            raise ValidationError("A file is required to be submitted with the name 'file'.")
        attrs['name'] = self.context['request'].FILES['file'].name
        return attrs