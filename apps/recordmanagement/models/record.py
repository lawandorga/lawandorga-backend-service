from django.apps import apps
from django.core.files import File

from apps.recordmanagement.models import EncryptedRecord, EncryptedClient
from apps.static.encryption import EncryptedModelMixin, AESEncryption, RSAEncryption
from rest_framework.reverse import reverse
from apps.api.models import Rlc, UserProfile, Group
from django.db import models
import json


###
# RecordTemplate
###
def get_default_show():
    return ['Token', 'State', 'Consultants', 'Tags', 'Official Note']


class RecordTemplate(models.Model):
    name = models.CharField(max_length=200)
    rlc = models.ForeignKey(Rlc, related_name='recordtemplates', on_delete=models.CASCADE, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    show = models.JSONField(default=get_default_show)

    class Meta:
        verbose_name = 'RecordTemplate'
        verbose_name_plural = 'RecordTemplates'

    def __str__(self):
        return 'recordTemplate: {}; rlc: {};'.format(self.pk, self.rlc)

    def get_field_types(self):
        return ['standard_fields', 'state_fields', 'users_fields', 'select_fields', 'multiple_fields',
                'encrypted_standard_fields', 'encrypted_select_fields', 'encrypted_file_fields']

    def get_fields(self, entry_types_and_serializers, request=None):
        # this might look weird, but i've done it this way to optimize performance
        # with prefetch related
        # and watch out this expects a self from a query which has prefetched
        # all the relevant unencrypted entries otherwise the queries explode
        fields = []
        for (field_type, serializer) in entry_types_and_serializers:
            for field in getattr(self, field_type).all():
                fields.append(serializer(instance=field, context={'request': request}).data)
        fields = list(sorted(fields, key=lambda i: i['order']))
        return fields


###
# RecordField
###
class RecordField(models.Model):
    name = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @property
    def type(self):
        raise NotImplemented('This property needs to be implemented.')

    @classmethod
    def get_entry_model(cls):
        name = cls.__name__.replace('Field', 'Entry')
        model = apps.get_model('recordmanagement', name)
        return model


class RecordStateField(RecordField):
    template = models.ForeignKey(RecordTemplate, on_delete=models.CASCADE, related_name='state_fields')
    options = models.JSONField(default=list)

    class Meta:
        verbose_name = 'RecordStateField'
        verbose_name_plural = 'RecordStateFields'

    @property
    def type(self):
        return 'select'

    def __str__(self):
        return 'recordStateField: {}; name: {};'.format(self.pk, self.name)


class RecordUsersField(RecordField):
    template = models.ForeignKey(RecordTemplate, on_delete=models.CASCADE, related_name='users_fields')
    share_keys = models.BooleanField(default=True)
    group = models.ForeignKey(Group, blank=True, null=True, default=None, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'RecordUsersField'
        verbose_name_plural = 'RecordUsersFields'

    @property
    def type(self):
        return 'multiple'

    def __str__(self):
        return 'recordUsersField: {}; name: {};'.format(self.pk, self.name)

    @property
    def options(self):
        if self.group:
            users = self.group.group_members.all()
        else:
            users = self.template.rlc.rlc_members.all()
        return [{'name': i[0], 'id': i[1]} for i in users.values_list('name', 'pk')]


class RecordSelectField(RecordField):
    template = models.ForeignKey(RecordTemplate, on_delete=models.CASCADE, related_name='select_fields')
    options = models.JSONField(default=list)

    class Meta:
        verbose_name = 'RecordSelectField'
        verbose_name_plural = 'RecordSelectFields'

    @property
    def type(self):
        return 'select'

    def __str__(self):
        return 'recordSelectField: {}; name: {};'.format(self.pk, self.name)


class RecordMultipleField(RecordField):
    template = models.ForeignKey(RecordTemplate, on_delete=models.CASCADE, related_name='multiple_fields')
    options = models.JSONField(default=list)

    class Meta:
        verbose_name = 'RecordMultipleField'
        verbose_name_plural = 'RecordMultipleFields'

    @property
    def type(self):
        return 'multiple'

    def __str__(self):
        return 'recordMultipleField: {}; name: {};'.format(self.pk, self.name)


class RecordEncryptedSelectField(RecordField):
    template = models.ForeignKey(RecordTemplate, on_delete=models.CASCADE, related_name='encrypted_select_fields')
    options = models.JSONField(default=list)

    class Meta:
        verbose_name = 'RecordEncryptedSelectField'
        verbose_name_plural = 'RecordEncryptedSelectFields'

    @property
    def type(self):
        return 'select'

    def __str__(self):
        return 'recordEncryptedSelectField: {}; name: {};'.format(self.pk, self.name)


class RecordEncryptedFileField(RecordField):
    template = models.ForeignKey(RecordTemplate, on_delete=models.CASCADE, related_name='encrypted_file_fields')

    class Meta:
        verbose_name = 'RecordEncryptedFileField'
        verbose_name_plural = 'RecordEncryptedFileFields'

    @property
    def type(self):
        return 'file'

    def __str__(self):
        return 'recordEncryptedFileField: {}; name: {};'.format(self.pk, self.name)


class RecordStandardField(RecordField):
    template = models.ForeignKey(RecordTemplate, on_delete=models.CASCADE, related_name='standard_fields')
    TYPE_CHOICES = (
        ('TEXTAREA', 'Multi Line'),
        ('TEXT', 'Single Line'),
        ('DATETIME-LOCAL', 'Date and Time'),
        ('DATE', 'Date'),
    )
    field_type = models.CharField(choices=TYPE_CHOICES, max_length=20, default='TEXT')

    class Meta:
        verbose_name = 'RecordStandardField'
        verbose_name_plural = 'RecordStandardFields'

    @property
    def type(self):
        return self.field_type.lower()

    def __str__(self):
        return 'recordStandardField: {}; name: {};'.format(self.pk, self.name)


class RecordEncryptedStandardField(RecordField):
    template = models.ForeignKey(RecordTemplate, on_delete=models.CASCADE, related_name='encrypted_standard_fields')
    TYPE_CHOICES = (
        ('TEXTAREA', 'Multi Line'),
        ('TEXT', 'Single Line'),
        ('DATE', 'Date')
    )
    field_type = models.CharField(choices=TYPE_CHOICES, max_length=20, default='TEXT')

    class Meta:
        verbose_name = 'RecordEncryptedStandardField'
        verbose_name_plural = 'RecordEncryptedStandardFields'

    @property
    def type(self):
        return self.field_type.lower()

    def __str__(self):
        return 'recordEncryptedStandardField: {}; name: {};'.format(self.pk, self.name)


###
# Record
###
class Record(models.Model):
    template = models.ForeignKey(RecordTemplate, related_name='records', on_delete=models.PROTECT)
    old_record = models.OneToOneField(EncryptedRecord, related_name='record', on_delete=models.SET_NULL, null=True,
                                      blank=True)
    old_client = models.ForeignKey(EncryptedClient, related_name='records', on_delete=models.SET_NULL, null=True,
                                   blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Record'
        verbose_name_plural = 'Records'

    def __str__(self):
        return 'record: {}; rlc: {};'.format(self.pk, self.template.rlc.name)

    @property
    def identifier(self):
        first_standard_entry = self.standard_entries.order_by('field__order').first()
        if first_standard_entry:
            return first_standard_entry.value
        return None

    def get_aes_key(self, user=None, private_key_user=None):
        if user and private_key_user:
            encryption = self.encryptions.get(user=user)
            encryption.decrypt(private_key_user)
            key = encryption.key
        else:
            raise ValueError('You need to pass (user and private_key_user).')
        return key

    def get_unencrypted_entry_types(self):
        return ['state_entries', 'standard_entries', 'select_entries', 'users_entries']

    def get_encrypted_entry_types(self):
        return ['encrypted_select_entries', 'encrypted_file_entries', 'encrypted_standard_entries']

    def get_all_entry_types(self):
        return self.get_unencrypted_entry_types() + self.get_encrypted_entry_types()

    def get_entries(self, entry_types_and_serializers, aes_key_record=None, request=None):
        # this might look weird, but i've done it this way to optimize performance
        # with prefetch related
        # and watch out this expects a self from a query which has prefetched
        # all the relevant unencrypted entries otherwise the queries explode
        entries = {}
        for (entry_type, serializer) in entry_types_and_serializers:
            for entry in getattr(self, entry_type).all():
                if entry.encrypted_entry:
                    entry.decrypt(aes_key_record=aes_key_record)
                entries[entry.field.name] = serializer(instance=entry, context={'request': request}).data
        entries = dict(sorted(entries.items(), key=lambda item: item[1]['order']))
        return entries

    def get_unencrypted_entries(self):
        return self.get_entries(self.get_unencrypted_entry_types())

    def get_encrypted_entries(self):
        return self.get_entries(self.get_encrypted_entry_types())

    def get_all_entries(self, *args, **kwargs):
        return self.get_entries(self.get_all_entry_types(), *args, **kwargs)


###
# RecordEntry
###
class RecordEntry(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # used in record for get_entries
    encrypted_entry = False

    class Meta:
        abstract = True

    def get_value(self, *args, **kwargs):
        raise NotImplementedError('This method needs to be implemented')


class RecordEntryEncryptedModelMixin(EncryptedModelMixin):
    encryption_class = AESEncryption

    # used in record for get entries
    encrypted_entry = True

    def encrypt(self, user=None, private_key_user=None, aes_key_record=None):
        if user and private_key_user:
            key = self.record.get_aes_key(user=user, private_key_user=private_key_user)
        elif aes_key_record:
            key = aes_key_record
        else:
            raise ValueError("You have to set (aes_key_record) or (user and private_key_user).")
        super().encrypt(key)

    def decrypt(self, user=None, private_key_user=None, aes_key_record=None):
        if user and private_key_user:
            key = self.record.get_aes_key(user=user, private_key_user=private_key_user)
        elif aes_key_record:
            key = aes_key_record
        else:
            raise ValueError("You have to set (aes_key_record) or (user and private_key_user).")
        super().decrypt(key)


class RecordStateEntry(RecordEntry):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='state_entries')
    field = models.ForeignKey(RecordStateField, related_name='entries', on_delete=models.PROTECT)
    value = models.CharField(max_length=1000)

    class Meta:
        unique_together = ['record', 'field']
        verbose_name = 'RecordStateEntry'
        verbose_name_plural = 'RecordStateEntries'

    def __str__(self):
        return 'recordStateEntry: {};'.format(self.pk)

    def get_value(self, *args, **kwargs):
        return self.value


class RecordUsersEntry(RecordEntry):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='users_entries')
    field = models.ForeignKey(RecordUsersField, related_name='entries', on_delete=models.PROTECT)
    value = models.ManyToManyField(UserProfile, blank=True)

    class Meta:
        unique_together = ['record', 'field']
        verbose_name = 'RecordUsersEntry'
        verbose_name_plural = 'RecordUsersEntries'

    def __str__(self):
        return 'recordUsersEntry: {};'.format(self.pk)

    def get_value(self, *args, **kwargs):
        # this might look weird, but i've done it this way to optimize performance
        # with prefetch related
        users = []
        for user in getattr(self, 'value').all():
            users.append(user.name)
        return users


class RecordSelectEntry(RecordEntry):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='select_entries')
    field = models.ForeignKey(RecordSelectField, related_name='entries', on_delete=models.PROTECT)
    value = models.CharField(max_length=200)

    class Meta:
        unique_together = ['record', 'field']
        verbose_name = 'RecordSelectEntry'
        verbose_name_plural = 'RecordSelectEntries'

    def __str__(self):
        return 'recordSelectEntry: {};'.format(self.pk)

    def get_value(self, *args, **kwargs):
        return self.value


class RecordMultipleEntry(RecordEntry):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='multiple_entries')
    field = models.ForeignKey(RecordMultipleField, related_name='entries', on_delete=models.PROTECT)
    value = models.JSONField()

    class Meta:
        unique_together = ['record', 'field']
        verbose_name = 'RecordMultipleEntry'
        verbose_name_plural = 'RecordMultipleEntries'

    def __str__(self):
        return 'recordMultipleEntry: {}'.format(self.pk)


class RecordEncryptedSelectEntry(RecordEntryEncryptedModelMixin, RecordEntry):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='encrypted_select_entries')
    field = models.ForeignKey(RecordEncryptedSelectField, related_name='entries', on_delete=models.PROTECT)
    value = models.BinaryField()

    # encryption
    encrypted_fields = ['value']

    class Meta:
        unique_together = ['record', 'field']
        verbose_name = 'RecordEncryptedSelectEntry'
        verbose_name_plural = 'RecordEncryptedSelectEntries'

    def __str__(self):
        return 'recordEncryptedSelectEntry: {};'.format(self.pk)

    def get_value(self, *args, **kwargs):
        if self.encryption_status == 'ENCRYPTED':
            self.decrypt(*args, **kwargs)
        return self.value

    def encrypt(self, *args, **kwargs):
        self.value = json.dumps(self.value)
        super().encrypt(*args, **kwargs)

    def decrypt(self, *args, **kwargs):
        super().decrypt(*args, **kwargs)
        self.value = json.loads(self.value)


class RecordEncryptedFileEntry(RecordEntry):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='encrypted_file_entries')
    field = models.ForeignKey(RecordEncryptedFileField, related_name='entries', on_delete=models.PROTECT)
    file = models.FileField(upload_to='recordmanagement/recordencryptedfileentry/')

    class Meta:
        unique_together = ['record', 'field']
        verbose_name = 'RecordEncryptedFileEntry'
        verbose_name_plural = 'RecordEncryptedFileEntries'

    def __str__(self):
        return 'recordEncryptedFileEntry: {};'.format(self.pk)

    def get_value(self, *args, **kwargs):
        return self.file.name.split('/')[-1].replace('.enc', '')

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)

    @staticmethod
    def encrypt_file(file, record, user=None, private_key_user=None, aes_key_record=None):
        if user and private_key_user:
            key = record.get_aes_key(user=user, private_key_user=private_key_user)
        elif aes_key_record:
            key = aes_key_record
        else:
            raise ValueError("You have to set (aes_key_record) or (user and private_key_user).")
        name = file.name
        file = AESEncryption.encrypt_in_memory_file(file, key)
        file = File(file, name='{}.enc'.format(name))
        return file

    def decrypt_file(self, user=None, private_key_user=None, aes_key_record=None):
        if user and private_key_user:
            key = self.record.get_aes_key(user=user, private_key_user=private_key_user)
        elif aes_key_record:
            key = aes_key_record
        else:
            raise ValueError("You have to set (aes_key_record) or (user and private_key_user).")
        file = AESEncryption.decrypt_bytes_file(self.file, key)
        file.seek(0)
        return file


class RecordStandardEntry(RecordEntry):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='standard_entries')
    field = models.ForeignKey(RecordStandardField, related_name='entries', on_delete=models.PROTECT)
    value = models.TextField(max_length=1000)

    class Meta:
        unique_together = ['record', 'field']
        verbose_name = 'RecordStandardEntry'
        verbose_name_plural = 'RecordStandardEntries'

    def __str__(self):
        return 'recordStandardEntry: {};'.format(self.pk)

    def get_value(self, *args, **kwargs):
        return self.value


class RecordEncryptedStandardEntry(RecordEntryEncryptedModelMixin, RecordEntry):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='encrypted_standard_entries')
    field = models.ForeignKey(RecordEncryptedStandardField, related_name='entries', on_delete=models.PROTECT)
    value = models.BinaryField()

    # encryption
    encryption_class = AESEncryption
    encrypted_fields = ['value']

    class Meta:
        unique_together = ['record', 'field']
        verbose_name = 'RecordStandardEntry'
        verbose_name_plural = 'RecordStandardEntries'

    def __str__(self):
        return 'recordEncryptedStandardEntry: {};'.format(self.pk)

    def get_value(self, *args, **kwargs):
        if self.encryption_status == 'ENCRYPTED' or self.encryption_status is None:
            self.decrypt(*args, **kwargs)
        return self.value


###
# RecordEncryption
###
class RecordEncryptionNew(EncryptedModelMixin, models.Model):
    user = models.ForeignKey(UserProfile, related_name="recordencryptions", on_delete=models.CASCADE)
    record = models.ForeignKey(Record, related_name="encryptions", on_delete=models.CASCADE)
    key = models.BinaryField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    encryption_class = RSAEncryption
    encrypted_fields = ["key"]

    class Meta:
        unique_together = ["user", "record"]
        verbose_name = "RecordEncryption"
        verbose_name_plural = "RecordEncryptions"

    def __str__(self):
        return "recordEncryption: {}; user: {}; record: {};".format(self.pk, self.user.email, self.record.pk)

    def decrypt(self, private_key_user=None):
        if private_key_user:
            key = private_key_user
        else:
            raise ValueError("You need to pass (private_key_user).")
        super().decrypt(key)

    def encrypt(self, public_key_user=None):
        if public_key_user:
            key = public_key_user
        else:
            raise ValueError('You need to pass (public_key_user).')
        super().encrypt(key)
