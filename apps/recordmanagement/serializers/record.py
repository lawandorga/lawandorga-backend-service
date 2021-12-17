from apps.recordmanagement.models.record import RecordTemplate, RecordField, RecordEncryptedStandardField, Record, RecordEncryptedStandardEntry, \
    RecordStandardEntry, RecordEncryptedFileEntry, RecordStandardField, RecordEncryptedFileField, RecordEncryptedSelectField, RecordEncryptedSelectEntry, \
    RecordUsersField, RecordUsersEntry, RecordStateField, RecordStateEntry, RecordSelectEntry, RecordSelectField
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
        if type(states) != list or any([type(s) is not str for s in states]):
            raise ValidationError('States need to be a list of strings.')
        if 'Closed' not in states:
            raise ValidationError('Closed needs to be added to states.')
        return states


class RecordSelectFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordSelectField
        fields = '__all__'

    def validate_options(self, options):
        if type(options) != list or any([type(o) is not str for o in options]):
            raise ValidationError('Options need to be a list of strings.')
        return options


class RecordEncryptedStandardFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordEncryptedStandardField
        fields = '__all__'


class RecordStandardFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordStandardField
        fields = '__all__'


class RecordUsersFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordUsersField
        fields = '__all__'


class RecordEncryptedFileFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordEncryptedFileField
        fields = '__all__'


class RecordEncryptedSelectFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordEncryptedSelectField
        fields = '__all__'

    def validate_options(self, options):
        if type(options) != list or any([type(o) is not str for o in options]):
            raise ValidationError('Options need to be a list of strings.')
        return options


###
# Entries
###
class RecordEncryptedFileEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordEncryptedFileEntry
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
        attrs['file'] = File(RecordEncryptedFileEntry.encrypt_file(file, record, user=user, private_key_user=private_key_user),
                             name='{}.enc'.format(file.name))
        return attrs


class RecordStandardEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordStandardEntry
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


class RecordEncryptedStandardEntrySerializer(serializers.ModelSerializer):
    text = serializers.CharField()

    class Meta:
        model = RecordEncryptedStandardEntry
        fields = '__all__'


class RecordEncryptedSelectEntrySerializer(serializers.ModelSerializer):
    value = serializers.JSONField()

    class Meta:
        model = RecordEncryptedSelectEntry
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


class RecordSelectEntrySerializer(serializers.ModelSerializer):
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


###
# Record
###
class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = '__all__'


class RecordListSerializer(RecordSerializer):
    standard_entries = RecordStandardEntrySerializer(many=True)
    entries = serializers.SerializerMethodField()
    state_entries = RecordStateEntrySerializer(many=True)

    def get_entries(self, obj):
        return obj.get_unencrypted_entries()
