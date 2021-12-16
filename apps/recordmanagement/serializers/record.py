from apps.recordmanagement.models.record import RecordTemplate, RecordField, RecordTextField, Record, RecordTextEntry, \
    RecordMetaEntry, RecordFileEntry, RecordMetaField, RecordFileField, RecordSelectField, RecordSelectEntry, \
    RecordUsersField, RecordUsersEntry, RecordStateField, RecordStateEntry
from rest_framework.exceptions import ValidationError
from django.core.files import File
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


class RecordStateFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordStateField
        fields = '__all__'

    def validate_states(self, states):
        if 'Closed' not in states:
            raise ValidationError('Closed needs to be added to states.')
        return states


class RecordTextFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordTextField
        fields = '__all__'


class RecordMetaFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordMetaField
        fields = '__all__'


class RecordUsersFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordUsersField
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


class RecordUsersEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordUsersEntry
        fields = '__all__'


class RecordStateEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordStateEntry
        fields = '__all__'

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance:
            field = self.instance.field
        elif 'field' in attrs:
            field = attrs['field']
        else:
            raise ValidationError('Field needs to be set.')
        if not attrs['state'] in field.states:
            raise ValidationError('The selected state is not allowed.')
        return attrs


class RecordTextEntrySerializer(serializers.ModelSerializer):
    text = serializers.CharField()

    class Meta:
        model = RecordTextEntry
        fields = '__all__'


class RecordSelectEntrySerializer(serializers.ModelSerializer):
    value = serializers.JSONField()

    class Meta:
        model = RecordSelectEntry
        fields = '__all__'

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance:
            field = self.instance.field
        elif 'field' in attrs:
            field = attrs['field']
        else:
            raise ValidationError('Field needs to be set.')
        if field.multiple is False and len(attrs['value']) > 1:
            raise ValidationError('Too many values selected.')
        if not (set(attrs['value']) <= set(field.options)):
            raise ValidationError('The selected values contain not allowed values.')
        return attrs
