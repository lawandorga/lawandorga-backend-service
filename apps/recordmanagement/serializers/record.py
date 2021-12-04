from apps.recordmanagement.models.record import RecordTemplate, RecordField, RecordTextField
from rest_framework import serializers


class RecordTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordTemplate
        fields = '__all__'

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs['rlc'] = self.context['request'].user.rlc
        return attrs


class RecordFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordField
        fields = '__all__'


class RecordTextFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordTextField
        fields = '__all__'
