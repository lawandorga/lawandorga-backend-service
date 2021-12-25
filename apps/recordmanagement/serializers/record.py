from apps.recordmanagement.models.record import RecordTemplate, RecordEncryptedStandardField, Record, \
    RecordEncryptedStandardEntry, RecordStandardEntry, RecordEncryptedFileEntry, RecordStandardField, \
    RecordEncryptedFileField, RecordEncryptedSelectField, RecordEncryptedSelectEntry, \
    RecordUsersField, RecordUsersEntry, RecordStateField, RecordStateEntry, RecordSelectEntry, RecordSelectField, \
    RecordMultipleEntry, RecordMultipleField
from rest_framework.exceptions import ValidationError, ParseError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.reverse import reverse
from django.core.files import File
from rest_framework import serializers


###
# RecordTemplate
###
from apps.recordmanagement.serializers import EncryptedClientSerializer


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
    url = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    entry_view_name = None

    def get_url(self, obj):
        return reverse(self.entry_view_name, request=self.context['request'])

    def get_type(self, obj):
        return obj.type

    def get_label(self, obj):
        return obj.name


class RecordStateFieldSerializer(RecordFieldSerializer):
    entry_view_name = 'recordstateentry-list'

    class Meta:
        model = RecordStateField
        fields = '__all__'

    def validate_options(self, options):
        if type(options) != list or any([type(s) is not str for s in options]):
            raise ValidationError('States need to be a list of strings.')
        if 'Closed' not in options:
            raise ValidationError('Closed needs to be added to states.')
        return options


class RecordSelectFieldSerializer(RecordFieldSerializer):
    entry_view_name = 'recordselectentry-list'

    class Meta:
        model = RecordSelectField
        fields = '__all__'

    def validate_options(self, options):
        if type(options) != list or any([type(o) is not str for o in options]):
            raise ValidationError('Options need to be a list of strings.')
        return options


class RecordMultipleFieldSerializer(RecordFieldSerializer):
    entry_view_name = 'recordmultipleentry-list'

    class Meta:
        model = RecordMultipleField
        fields = '__all__'

    def validate_options(self, options):
        if type(options) != list or any([type(o) is not str for o in options]):
            raise ValidationError('Options need to be a list of strings.')
        return options


class RecordEncryptedStandardFieldSerializer(RecordFieldSerializer):
    entry_view_name = 'recordencryptedstandardentry-list'

    class Meta:
        model = RecordEncryptedStandardField
        fields = '__all__'


class RecordStandardFieldSerializer(RecordFieldSerializer):
    entry_view_name = 'recordstandardentry-list'

    class Meta:
        model = RecordStandardField
        fields = '__all__'


class RecordUsersFieldSerializer(RecordFieldSerializer):
    entry_view_name = 'recordusersentry-list'
    options = serializers.JSONField(read_only=True)

    class Meta:
        model = RecordUsersField
        fields = '__all__'


class RecordEncryptedFileFieldSerializer(RecordFieldSerializer):
    entry_view_name = 'recordencryptedfileentry-list'

    class Meta:
        model = RecordEncryptedFileField
        fields = '__all__'


class RecordEncryptedSelectFieldSerializer(RecordFieldSerializer):
    entry_view_name = 'recordencryptedselectentry-list'

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
class RecordEntrySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    order = serializers.SerializerMethodField(read_only=True)

    def get_order(self, obj):
        return obj.field.order

    def get_name(self, obj):
        return obj.field.name

    def get_type(self, obj):
        return obj.field.type


class RecordEncryptedFileEntrySerializer(RecordEntrySerializer):
    url = serializers.HyperlinkedIdentityField(view_name='recordencryptedfileentry-detail')

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
        attrs['file'] = File(
            RecordEncryptedFileEntry.encrypt_file(file, record, user=user, private_key_user=private_key_user),
            name='{}.enc'.format(file.name))
        return attrs


class RecordStandardEntrySerializer(RecordEntrySerializer):
    url = serializers.HyperlinkedIdentityField(view_name='recordstandardentry-detail')

    class Meta:
        model = RecordStandardEntry
        fields = '__all__'


class RecordUsersEntrySerializer(RecordEntrySerializer):
    url = serializers.HyperlinkedIdentityField(view_name='recordusersentry-detail')

    class Meta:
        model = RecordUsersEntry
        fields = '__all__'


class RecordUsersEntryDetailSerializer(RecordUsersEntrySerializer):
    url = serializers.HyperlinkedIdentityField(view_name='recordusersentry-detail')
    value = serializers.SerializerMethodField()

    def get_value(self, obj):
        return obj.get_value()


class RecordStateEntrySerializer(RecordEntrySerializer):
    url = serializers.HyperlinkedIdentityField(view_name='recordstateentry-detail')

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
        if not attrs['value'] in field.options:
            raise ValidationError('The selected state is not allowed.')
        return attrs


class RecordEncryptedStandardEntrySerializer(RecordEntrySerializer):
    value = serializers.CharField()
    url = serializers.HyperlinkedIdentityField(view_name='recordencryptedstandardentry-detail')

    class Meta:
        model = RecordEncryptedStandardEntry
        fields = '__all__'


class RecordEncryptedSelectEntrySerializer(RecordEntrySerializer):
    url = serializers.HyperlinkedIdentityField(view_name='recordencryptedselectentry-detail')
    value = serializers.CharField()

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
        if attrs['value'] not in set(field.options):
            raise ValidationError('The selected value is not a valid choice.')
        return attrs


class RecordSelectEntrySerializer(RecordEntrySerializer):
    url = serializers.HyperlinkedIdentityField(view_name='recordselectentry-detail')

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
        if attrs['value'] not in set(field.options):
            raise ValidationError('The selected value is not a valid choice.')
        return attrs


class RecordMultipleEntrySerializer(RecordEntrySerializer):
    url = serializers.HyperlinkedIdentityField(view_name='recordmultipleentry-detail')

    class Meta:
        model = RecordMultipleEntry
        fields = '__all__'

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance:
            field = self.instance.field
        elif 'field' in attrs:
            field = attrs['field']
        else:
            raise ValidationError('Field needs to be set.')
        if not (set(attrs['value']) <= set(field.options)):
            raise ValidationError('The selected values contain not allowed values.')
        return attrs


###
# Record
###
class RecordSerializer(serializers.ModelSerializer):
    # delete = serializers.SerializerMethodField()

    class Meta:
        model = Record
        fields = '__all__'

    # def get_delete(self, obj):
    #     return obj.deletions_requested.filter(state='re').exists()


class RecordListSerializer(RecordSerializer):
    entries = serializers.SerializerMethodField()
    access = serializers.SerializerMethodField()
    show = serializers.SerializerMethodField()

    def get_entries(self, obj):
        entry_types = [
            ('state_entries', RecordStateEntrySerializer),
            ('standard_entries', RecordStandardEntrySerializer),
            ('select_entries', RecordSelectEntrySerializer),
            ('multiple_entries', RecordMultipleEntrySerializer),
            ('users_entries', RecordUsersEntryDetailSerializer),
        ]
        return obj.get_entries(entry_types, request=self.context['request'])

    def get_access(self, obj):
        for enc in getattr(obj, 'encryptions').all():
            if enc.user_id == self.context['request'].user.id:
                return True
        return False

    def get_show(self, obj):
        return obj.template.show


class RecordCreateSerializer(RecordListSerializer):
    pass


class RecordDetailSerializer(RecordSerializer):
    entries = serializers.SerializerMethodField()
    fields = serializers.SerializerMethodField(method_name='get_form_fields')
    client = serializers.SerializerMethodField()
    url = serializers.HyperlinkedIdentityField(view_name='record-detail')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context['request']
        self.user = request.user
        self.private_key_user = self.user.get_private_key(request=request)
        self.private_key_rlc = self.user.rlc.get_private_key(user=self.user, private_key_user=self.private_key_user)

    def get_entries(self, obj):
        try:
            aes_key_record = self.instance.get_aes_key(user=self.user, private_key_user=self.private_key_user)
        except ObjectDoesNotExist:
            raise ParseError('No encryption keys were found to decrypt this record.')
        entry_types_and_serializers = [
            ('state_entries', RecordStateEntrySerializer),
            ('standard_entries', RecordStandardEntrySerializer),
            ('select_entries', RecordSelectEntrySerializer),
            ('multiple_entries', RecordMultipleEntrySerializer),
            ('users_entries', RecordUsersEntrySerializer),
            ('encrypted_select_entries', RecordEncryptedSelectEntrySerializer),
            ('encrypted_file_entries', RecordEncryptedFileEntrySerializer),
            ('encrypted_standard_entries', RecordEncryptedStandardEntrySerializer)
        ]
        return obj.get_entries(entry_types_and_serializers, aes_key_record=aes_key_record, request=self.context['request'])

    def get_form_fields(self, obj):
        field_types_and_serializers = [
            ('state_fields', RecordStateFieldSerializer),
            ('standard_fields', RecordStandardFieldSerializer),
            ('select_fields', RecordSelectFieldSerializer),
            ('multiple_fields', RecordMultipleFieldSerializer),
            ('users_fields', RecordUsersFieldSerializer),
            ('encrypted_standard_fields', RecordEncryptedStandardFieldSerializer),
            ('encrypted_select_fields', RecordEncryptedSelectFieldSerializer),
            ('encrypted_file_fields', RecordEncryptedFileFieldSerializer)
        ]
        return obj.template.get_fields(field_types_and_serializers, request=self.context['request'])

    def get_client(self, obj):
        if obj.old_client is None:
            return {}
        obj.old_client.decrypt(private_key_rlc=self.private_key_rlc)
        return EncryptedClientSerializer(instance=obj.old_client).data