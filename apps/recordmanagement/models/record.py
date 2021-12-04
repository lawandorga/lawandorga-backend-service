from apps.recordmanagement.models.encrypted_record import EncryptedRecord
from apps.static.encryption import EncryptedModelMixin, AESEncryption, RSAEncryption
from apps.api.models import Rlc, UserProfile
from django.db import models


class RecordTemplate(models.Model):
    name = models.CharField(max_length=200)
    rlc = models.ForeignKey(Rlc, related_name='recordtemplates', on_delete=models.CASCADE, blank=True)

    class Meta:
        verbose_name = 'RecordTemplate'
        verbose_name_plural = 'RecordTemplates'


class RecordField(models.Model):
    name = models.CharField(max_length=200)
    template = models.ForeignKey(RecordTemplate, on_delete=models.CASCADE, related_name='fields')

    class Meta:
        abstract = True

    @property
    def type(self):
        raise NotImplemented('This property needs to be implemented.')


class RecordFileField(RecordField):
    class Meta:
        verbose_name = 'RecordFileField'
        verbose_name_plural = 'RecordFileFields'

    @property
    def type(self):
        return 'file'


class RecordTextField(RecordField):
    TYPE_CHOICES = (
        ('textarea', 'Multi Line'),
        ('text', 'Single Line')
    )
    type = models.CharField(choices=TYPE_CHOICES, max_length=20)

    class Meta:
        verbose_name = 'RecordTextField'
        verbose_name_plural = 'RecordTextFields'

    @property
    def type(self):
        return self.type


class Record(models.Model):
    template = models.ForeignKey(RecordTemplate, related_name='records', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Record'
        verbose_name_plural = 'Records'

    def get_decryption_key(self, user, private_key_user):
        encryption = self.encryptions.get(user=user, private_key_user=private_key_user)  # TODO
        encryption.decrypt(private_key_user)
        key = encryption.encrypted_key
        return key


class RecordFieldEntry(models.Model):
    field = models.ForeignKey(RecordField, related_name='entries', on_delete=models.PROTECT)
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='entries')

    class Meta:
        abstract = True


class RecordTextFieldEntry(EncryptedModelMixin, RecordFieldEntry):
    text = models.BinaryField()

    # encryption
    encryption_class = AESEncryption
    encrypted_fields = ['text']

    class Meta:
        verbose_name = 'RecordTextFieldEntry'
        verbose_name_plural = 'RecordTextFieldEntries'

    def decrypt(self, user=None, private_key_user=None):
        if user and private_key_user:
            key = self.record.get_decryption_key(user=user, private_key_user=private_key_user)
        else:
            raise ValueError("You have to set (user and private_key_user).")
        super().decrypt(key)


class RecordFileFieldEntry(RecordFieldEntry):
    file = models.FileField(upload_to='recordfilefield/')

    class Meta:
        verbose_name = 'RecordFileFieldEntry'
        verbose_name_plural = 'RecordFileFieldEntries'


# encryption
class RecordEncryption(EncryptedModelMixin, models.Model):
    user = models.ForeignKey(UserProfile, related_name="recordencryptions", on_delete=models.CASCADE)
    record = models.ForeignKey(EncryptedRecord, related_name="encryptions", on_delete=models.CASCADE)
    key = models.BinaryField()
    encryption_class = RSAEncryption
    encrypted_fields = ["key"]

    class Meta:
        unique_together = ("user", "record")
        verbose_name = "RecordEncryption"
        verbose_name_plural = "RecordEncryptions"

    def __str__(self):
        return "recordEncryption: {}; user: {}; record: {};".format(self.id, self.user.email, self.record.record_token)

    def decrypt(self, private_key_user=None):
        if private_key_user:
            key = private_key_user
        else:
            raise ValueError("You need to pass (private_key_user).")
        super().decrypt(key)

    def get_key(self, private_key_user):
        if not self.key:
            raise ValueError("This RecordEncryption does not have an encrypted key.")
        return RSAEncryption.decrypt(self.key, private_key_user)
