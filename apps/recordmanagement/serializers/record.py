from django.core.files import File
from rest_framework.exceptions import ValidationError

from apps.recordmanagement.models.record import RecordTemplate, RecordField, RecordTextField, Record, RecordTextEntry, \
    RecordMetaEntry, RecordFileEntry, RecordMetaField, RecordFileField, RecordSelectField, RecordSelectEntry
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


class RecordMetaFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordMetaField
        fields = '__all__'


class RecordFileFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordFileField
        fields = '__all__'


class RecordSelectFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordSelectField
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
class RecordFileEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordFileEntry
        fields = '__all__'

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if 'file' in attrs:
            file = attrs['file']
        else:
            raise ValidationError('A file needs to be submitted.')
        user = self.context['request'].user
        if self.instance:
            record = self.instance.record
        else:
            if 'record' in attrs:
                record = attrs['record']
            else:
                raise ValidationError('A record needs to be set.')
        private_key_user = user.get_private_key(request=self.context['request'])
        attrs['file'] = File(RecordFileEntry.encrypt_file(file, record, user=user, private_key_user=private_key_user),
                             name='{}.enc'.format(file.name))
        return attrs


class RecordMetaEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordMetaEntry
        fields = '__all__'


class RecordTextEntrySerializer(serializers.ModelSerializer):
    text = serializers.CharField()

    class Meta:
        model = RecordTextEntry
        fields = '__all__'


class RecordSelectEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordSelectEntry
        fields = '__all__'
