from apps.static.encryption import EncryptedModelMixin, AESEncryption, RSAEncryption
from apps.api.models import Rlc, UserProfile
from django.db import models


###
# RecordTemplate
###
from apps.static.storage import download_and_decrypt_file, encrypt_and_upload_file


class RecordTemplate(models.Model):
    name = models.CharField(max_length=200)
    rlc = models.ForeignKey(Rlc, related_name='recordtemplates', on_delete=models.CASCADE, blank=True)

    class Meta:
        verbose_name = 'RecordTemplate'
        verbose_name_plural = 'RecordTemplates'


###
# RecordField
###
class RecordField(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        abstract = True

    @property
    def type(self):
        raise NotImplemented('This property needs to be implemented.')


class RecordSelectField(RecordField):
    template = models.ForeignKey(RecordTemplate, on_delete=models.CASCADE, related_name='select_fields')
    multiple = models.BooleanField(default=False)
    options = models.JSONField()

    class Meta:
        verbose_name = 'RecordSelectField'
        verbose_name_plural = 'RecordSelectFields'

    @property
    def type(self):
        return 'select'


class RecordFileField(RecordField):
    template = models.ForeignKey(RecordTemplate, on_delete=models.CASCADE, related_name='file_fields')

    class Meta:
        verbose_name = 'RecordFileField'
        verbose_name_plural = 'RecordFileFields'

    @property
    def type(self):
        return 'file'


class RecordMetaField(RecordField):
    template = models.ForeignKey(RecordTemplate, on_delete=models.CASCADE, related_name='meta_fields')

    class Meta:
        verbose_name = 'RecordMetaField'
        verbose_name_plural = 'RecordMetaFields'

    @property
    def type(self):
        return 'text'


class RecordTextField(RecordField):
    template = models.ForeignKey(RecordTemplate, on_delete=models.CASCADE, related_name='text_fields')
    TYPE_CHOICES = (
        ('TEXTAREA', 'Multi Line'),
        ('TEXT', 'Single Line')
    )
    field_type = models.CharField(choices=TYPE_CHOICES, max_length=20)

    class Meta:
        verbose_name = 'RecordTextField'
        verbose_name_plural = 'RecordTextFields'

    @property
    def type(self):
        return self.field_type.lower()


###
# Record
###
class Record(models.Model):
    template = models.ForeignKey(RecordTemplate, related_name='records', on_delete=models.PROTECT)

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


class RecordSelectEntry(RecordEntryEncryptedModelMixin, RecordEntry):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='select_entries')
    field = models.ForeignKey(RecordSelectField, related_name='entries', on_delete=models.PROTECT)
    value = models.BinaryField()

    # encryption
    encrypted_fields = ['value']

    class Meta:
        unique_together = ['record', 'field']
        verbose_name = 'RecordSelectEntry'
        verbose_name_plural = 'RecordSelectEntries'

    def __str__(self):
        return 'recordSelectEntry: {};'.format(self.pk)


class RecordFileEntry(RecordEntry):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='file_entries')
    field = models.ForeignKey(RecordFileField, related_name='entries', on_delete=models.PROTECT)
    file = models.FileField(upload_to='recordfileentry/')

    class Meta:
        unique_together = ['record', 'field']
        verbose_name = 'RecordFileEntry'
        verbose_name_plural = 'RecordFileEntries'

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


class RecordMetaEntry(RecordEntry):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='meta_entries')
    field = models.ForeignKey(RecordMetaField, related_name='entries', on_delete=models.PROTECT)
    text = models.CharField(max_length=500)

    class Meta:
        unique_together = ['record', 'field']
        verbose_name = 'RecordMetaEntry'
        verbose_name_plural = 'RecordMetaEntries'

    def __str__(self):
        return 'recordMetaEntry: {};'.format(self.pk)


class RecordTextEntry(RecordEntryEncryptedModelMixin, RecordEntry):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='text_entries')
    field = models.ForeignKey(RecordTextField, related_name='entries', on_delete=models.PROTECT)
    text = models.BinaryField()

    # encryption
    encryption_class = AESEncryption
    encrypted_fields = ['text']

    class Meta:
        unique_together = ['record', 'field']
        verbose_name = 'RecordTextFieldEntry'
        verbose_name_plural = 'RecordTextFieldEntries'

    def __str__(self):
        return 'recordTextEntry: {};'.format(self.pk)


###
# RecordEncryption
###
class RecordEncryptionNew(EncryptedModelMixin, models.Model):
    user = models.ForeignKey(UserProfile, related_name="recordencryptions", on_delete=models.CASCADE)
    record = models.ForeignKey(Record, related_name="encryptions", on_delete=models.CASCADE)
    key = models.BinaryField()
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
