from apps.recordmanagement.models.record import RecordTemplate, RecordField, RecordTextField, Record, RecordTextEntry, \
    RecordMetaEntry
from rest_framework import serializers


###
# RecordTemplate
###
class RecordTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordTemplate
        fields = '__all__'

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs['rlc'] = self.context['request'].user.rlc
        return attrs


###
# Fields
###
class RecordFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordField
        fields = '__all__'


class RecordTextFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordTextField
        fields = '__all__'


###
# Record
###
class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = '__all__'


###
# Entries
###
class RecordMetaEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordMetaEntry
        fields = '__all__'


class RecordTextEntrySerializer(serializers.ModelSerializer):
    text = serializers.CharField()

    class Meta:
        model = RecordTextEntry
        fields = '__all__'
