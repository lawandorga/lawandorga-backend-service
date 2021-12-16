from apps.recordmanagement.models import EncryptedRecord
from apps.static.encryption import EncryptedModelMixin, AESEncryption, RSAEncryption
from apps.api.models import Rlc, UserProfile
from django.db import models
import json


###
# RecordTemplate
###
class RecordTemplate(models.Model):
    name = models.CharField(max_length=200)
    rlc = models.ForeignKey(Rlc, related_name='recordtemplates', on_delete=models.CASCADE, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'RecordTemplate'
        verbose_name_plural = 'RecordTemplates'

    def __str__(self):
        return 'recordTemplate: {}; rlc: {};'.format(self.pk, self.rlc)


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


class RecordStateField(RecordField):
    template = models.OneToOneField(RecordTemplate, on_delete=models.CASCADE, related_name='state_fields')
    states = models.JSONField()

    class Meta:
        verbose_name = 'RecordStateField'
        verbose_name_plural = 'RecordStateFields'

    @property
    def type(self):
        return 'select'


class RecordUsersField(RecordField):
    template = models.ForeignKey(RecordTemplate, on_delete=models.CASCADE, related_name='users_fields')

    class Meta:
        verbose_name = 'RecordUsersField'
        verbose_name_plural = 'RecordUsersFields'

    @property
    def type(self):
        return 'select'


class RecordSelectField(RecordField):
    template = models.ForeignKey(RecordTemplate, on_delete=models.CASCADE, related_name='multiple_fields')
    options = models.JSONField()
    multiple = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'RecordSelectField'
        verbose_name_plural = 'RecordSelectFields'

    @property
    def type(self):
        return 'multiple'


class RecordEncryptedSelectField(RecordField):
    template = models.ForeignKey(RecordTemplate, on_delete=models.CASCADE, related_name='select_fields')
    multiple = models.BooleanField(default=False)
    options = models.JSONField()

    class Meta:
        verbose_name = 'RecordEncryptedSelectField'
        verbose_name_plural = 'RecordEncryptedSelectFields'

    @property
    def type(self):
        return 'select'


class RecordEncryptedFileField(RecordField):
    template = models.ForeignKey(RecordTemplate, on_delete=models.CASCADE, related_name='file_fields')

    class Meta:
        verbose_name = 'RecordEncryptedFileField'
        verbose_name_plural = 'RecordEncryptedFileFields'

    @property
    def type(self):
        return 'file'


class RecordStandardField(RecordField):
    template = models.ForeignKey(RecordTemplate, on_delete=models.CASCADE, related_name='meta_fields')
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


class RecordEncryptedStandardField(RecordField):
    template = models.ForeignKey(RecordTemplate, on_delete=models.CASCADE, related_name='text_fields')
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


###
# Record
###
class Record(models.Model):
    template = models.ForeignKey(RecordTemplate, related_name='records', on_delete=models.PROTECT)
    old_record = models.OneToOneField(EncryptedRecord, related_name='record', on_delete=models.SET_NULL, null=True,
                                      blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Record'
        verbose_name_plural = 'Records'

    def get_aes_key(self, user, private_key_user):
        encryption = self.encryptions.get(user=user, record=self)
        encryption.decrypt(private_key_user)
        key = encryption.key
        return key


###
# RecordEntry
###
class RecordEntry(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class RecordEntryEncryptedModelMixin(EncryptedModelMixin):
    encryption_class = AESEncryption

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
    state = models.CharField(max_length=1000)

    class Meta:
        unique_together = ['record', 'field']
        verbose_name = 'RecordStateEntry'
        verbose_name_plural = 'RecordStateEntries'

    def __str__(self):
        return 'recordStateEntry: {};'.format(self.pk)


class RecordUsersEntry(RecordEntry):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='users_entries')
    field = models.ForeignKey(RecordUsersField, related_name='entries', on_delete=models.PROTECT)
    users = models.ManyToManyField(UserProfile, blank=True)

    class Meta:
        unique_together = ['record', 'field']
        verbose_name = 'RecordUsersEntry'
        verbose_name_plural = 'RecordUsersEntries'

    def __str__(self):
        return 'recordUsersEntry: {};'.format(self.pk)


class RecordSelectEntry(RecordEntry):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='multiple_entries')
    field = models.ForeignKey(RecordSelectField, related_name='entries', on_delete=models.PROTECT)
    value = models.JSONField()

    class Meta:
        unique_together = ['record', 'field']
        verbose_name = 'RecordSelectEntry'
        verbose_name_plural = 'RecordSelectEntries'

    def __str__(self):
        return 'recordSelectEntry: {};'.format(self.pk)


class RecordEncryptedSelectEntry(RecordEntryEncryptedModelMixin, RecordEntry):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='select_entries')
    field = models.ForeignKey(RecordEncryptedSelectField, related_name='entries', on_delete=models.PROTECT)
    value = models.BinaryField()

    # encryption
    encrypted_fields = ['value']

    class Meta:
        unique_together = ['record', 'field']
        verbose_name = 'RecordEncryptedSelectEntry'
        verbose_name_plural = 'RecordEncryptedSelectEntries'

    def __str__(self):
        return 'recordSelectEntry: {};'.format(self.pk)

    def encrypt(self, *args, **kwargs):
        self.value = json.dumps(self.value)
        super().encrypt(*args, **kwargs)

    def decrypt(self, *args, **kwargs):
        super().decrypt(*args, **kwargs)
        self.value = json.loads(self.value)


class RecordEncryptedFileEntry(RecordEntry):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='file_entries')
    field = models.ForeignKey(RecordEncryptedFileField, related_name='entries', on_delete=models.PROTECT)
    file = models.FileField(upload_to='recordfileentry/')

    class Meta:
        unique_together = ['record', 'field']
        verbose_name = 'RecordEncryptedFileEntry'
        verbose_name_plural = 'RecordEncryptedFileEntries'

    def __str__(self):
        return 'recordFileEntry: {};'.format(self.pk)

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
        file = AESEncryption.encrypt_in_memory_file(file, key)
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
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='meta_entries')
    field = models.ForeignKey(RecordStandardField, related_name='entries', on_delete=models.PROTECT)
    text = models.CharField(max_length=500)

    class Meta:
        unique_together = ['record', 'field']
        verbose_name = 'RecordStandardEntry'
        verbose_name_plural = 'RecordStandardEntries'

    def __str__(self):
        return 'recordStandardEntry: {};'.format(self.pk)


class RecordEncryptedStandardEntry(RecordEntryEncryptedModelMixin, RecordEntry):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='text_entries')
    field = models.ForeignKey(RecordEncryptedStandardField, related_name='entries', on_delete=models.PROTECT)
    text = models.BinaryField()

    # encryption
    encryption_class = AESEncryption
    encrypted_fields = ['text']

    class Meta:
        unique_together = ['record', 'field']
        verbose_name = 'RecordStandardEntry'
        verbose_name_plural = 'RecordStandardEntries'

    def __str__(self):
        return 'recordStandardEntry: {};'.format(self.pk)


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

    def get_key(self, private_key_user):
        if not self.key:
            raise ValueError("This RecordEncryption does not have an encrypted key.")
        return RSAEncryption.decrypt(self.key, private_key_user)
