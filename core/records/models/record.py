import json
from typing import Optional, Union

from django.apps import apps
from django.core.files import File as DjangoFile
from django.db import models
from django.utils.timezone import localtime

from core.auth.models import RlcUser
from core.models import Group, Org
from core.records.models import EncryptedClient  # type: ignore
from core.seedwork.encryption import AESEncryption, EncryptedModelMixin, RSAEncryption


###
# RecordTemplate
###
def get_default_show():
    return ["Token", "State", "Consultants", "Tags", "Official Note"]


class RecordTemplate(models.Model):
    name = models.CharField(max_length=200)
    rlc = models.ForeignKey(
        Org, related_name="recordtemplates", on_delete=models.CASCADE, blank=True
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    show = models.JSONField(default=get_default_show)

    class Meta:
        verbose_name = "RecordTemplate"
        verbose_name_plural = "RecordTemplates"

    def __str__(self):
        return "recordTemplate: {}; rlc: {};".format(self.pk, self.rlc)

    def get_field_types(self):
        return [
            "standard_fields",
            "state_fields",
            "users_fields",
            "select_fields",
            "multiple_fields",
            "encrypted_standard_fields",
            "encrypted_select_fields",
            "encrypted_file_fields",
        ]

    def get_fields(self, entry_types_and_serializers, request=None):
        # this might look weird, but i've done it this way to optimize performance
        # with prefetch related
        # and watch out this expects a self from a query which has prefetched
        # all the relevant unencrypted entries otherwise the queries explode
        fields = []
        for (field_type, serializer) in entry_types_and_serializers:
            for field in getattr(self, field_type).all():
                fields.append(
                    serializer(instance=field, context={"request": request}).data
                )
        fields = list(sorted(fields, key=lambda i: i["order"]))
        return fields

    @classmethod
    def get_statistic_fields_meta(cls):
        from core.records.fixtures import get_all_countries

        return [
            {
                "name": "Nationality of the client",
                "options": get_all_countries(),
                "order": 99100,
                "helptext": "",
            },
            {
                "name": "Age in years of the client",
                "options": [
                    "0-10",
                    "11-20",
                    "21-30",
                    "31-40",
                    "41-50",
                    "51-60",
                    "61-70",
                    "71-80",
                    "81-90",
                    "90+",
                    "Unknown",
                ],
                "order": 99200,
                "helptext": "",
            },
            {
                "name": "Sex of the client",
                "options": ["Male", "Female", "Other", "Unknown"],
                "order": 99300,
                "helptext": "",
            },
            {
                "name": "Current status of the client",
                "options": [
                    "Employed",
                    "University Student",
                    "Apprentice",
                    "Unemployed",
                    "Pensioner",
                    "Other",
                    "Unknown",
                ],
                "order": 99400,
                "helptext": "A person has migration background if one or both parents were not "
                "born with a German citizenship. (Source: Statistisches Bundesamt)",
            },
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for field in self.get_statistic_fields_meta():
            if not RecordStatisticField.objects.filter(
                name=field["name"], template=self
            ).exists():
                RecordStatisticField.objects.create(template=self, **field)


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
        raise NotImplementedError("This property needs to be implemented.")

    @classmethod
    def get_entry_model(cls):
        name = cls.__name__.replace("Field", "Entry")
        model = apps.get_model("core", name)
        return model


class RecordStateField(RecordField):
    template = models.ForeignKey(
        RecordTemplate, on_delete=models.CASCADE, related_name="state_fields"
    )
    options = models.JSONField(default=list)

    class Meta:
        verbose_name = "RecordStateField"
        verbose_name_plural = "RecordStateFields"

    @property
    def type(self):
        return "select"

    def __str__(self):
        return "recordStateField: {}; name: {};".format(self.pk, self.name)


class RecordUsersField(RecordField):
    template = models.ForeignKey(
        RecordTemplate, on_delete=models.CASCADE, related_name="users_fields"
    )
    share_keys = models.BooleanField(default=True)
    group = models.ForeignKey(
        Group, blank=True, null=True, default=None, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = "RecordUsersField"
        verbose_name_plural = "RecordUsersFields"

    @property
    def type(self):
        return "multiple"

    def __str__(self):
        return "recordUsersField: {}; name: {};".format(self.pk, self.name)

    @property
    def options(self):
        if self.group:
            users = list(self.group.members.all())
        else:
            users = list(self.template.rlc.users.all())

        return [{"name": i.name, "id": i.pk} for i in users]


class RecordSelectField(RecordField):
    template = models.ForeignKey(
        RecordTemplate, on_delete=models.CASCADE, related_name="select_fields"
    )
    options = models.JSONField(default=list)

    class Meta:
        verbose_name = "RecordSelectField"
        verbose_name_plural = "RecordSelectFields"

    @property
    def type(self):
        return "select"

    def __str__(self):
        return "recordSelectField: {}; name: {};".format(self.pk, self.name)


class RecordMultipleField(RecordField):
    template = models.ForeignKey(
        RecordTemplate, on_delete=models.CASCADE, related_name="multiple_fields"
    )
    options = models.JSONField(default=list)

    class Meta:
        verbose_name = "RecordMultipleField"
        verbose_name_plural = "RecordMultipleFields"

    @property
    def type(self):
        return "multiple"

    def __str__(self):
        return "recordMultipleField: {}; name: {};".format(self.pk, self.name)


class RecordEncryptedSelectField(RecordField):
    template = models.ForeignKey(
        RecordTemplate, on_delete=models.CASCADE, related_name="encrypted_select_fields"
    )
    options = models.JSONField(default=list)

    class Meta:
        verbose_name = "RecordEncryptedSelectField"
        verbose_name_plural = "RecordEncryptedSelectFields"

    @property
    def type(self):
        return "select"

    def __str__(self):
        return "recordEncryptedSelectField: {}; name: {};".format(self.pk, self.name)


class RecordEncryptedFileField(RecordField):
    template = models.ForeignKey(
        RecordTemplate, on_delete=models.CASCADE, related_name="encrypted_file_fields"
    )

    class Meta:
        verbose_name = "RecordEncryptedFileField"
        verbose_name_plural = "RecordEncryptedFileFields"

    @property
    def type(self):
        return "file"

    def __str__(self):
        return "recordEncryptedFileField: {}; name: {};".format(self.pk, self.name)


class RecordStandardField(RecordField):
    template = models.ForeignKey(
        RecordTemplate, on_delete=models.CASCADE, related_name="standard_fields"
    )
    TYPE_CHOICES = (
        ("TEXTAREA", "Multi Line"),
        ("TEXT", "Single Line"),
        ("DATETIME-LOCAL", "Date and Time"),
        ("DATE", "Date"),
    )
    field_type = models.CharField(choices=TYPE_CHOICES, max_length=20, default="TEXT")

    class Meta:
        verbose_name = "RecordStandardField"
        verbose_name_plural = "RecordStandardFields"

    @property
    def type(self):
        return self.field_type.lower()

    def __str__(self):
        return "recordStandardField: {}; name: {};".format(self.pk, self.name)


class RecordEncryptedStandardField(RecordField):
    template = models.ForeignKey(
        RecordTemplate,
        on_delete=models.CASCADE,
        related_name="encrypted_standard_fields",
    )
    TYPE_CHOICES = (
        ("TEXTAREA", "Multi Line"),
        ("TEXT", "Single Line"),
        ("DATE", "Date"),
    )
    field_type = models.CharField(choices=TYPE_CHOICES, max_length=20, default="TEXT")

    class Meta:
        verbose_name = "RecordEncryptedStandardField"
        verbose_name_plural = "RecordEncryptedStandardFields"

    @property
    def type(self):
        return self.field_type.lower()

    def __str__(self):
        return "recordEncryptedStandardField: {}; name: {};".format(self.pk, self.name)


class RecordStatisticField(RecordField):
    template = models.ForeignKey(
        RecordTemplate, on_delete=models.CASCADE, related_name="statistic_fields"
    )
    options = models.JSONField(default=list)
    helptext = models.CharField(max_length=1000)

    class Meta:
        verbose_name = "RecordStatisticField"
        verbose_name_plural = "RecordStatisticFields"

    @property
    def type(self):
        return "select"

    def __str__(self):
        return "recordStatisticField: {}; name: {};".format(self.pk, self.name)


###
# Record
###
class Record(models.Model):
    template = models.ForeignKey(
        RecordTemplate, related_name="records", on_delete=models.PROTECT
    )
    old_client = models.ForeignKey(
        EncryptedClient,
        related_name="records",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Record"
        verbose_name_plural = "Records"

    def __str__(self):
        return "record: {}; rlc: {};".format(self.pk, self.template.rlc.name)

    @property
    def identifier(self):
        first_standard_entry = self.standard_entries.order_by("field__order").first()
        if first_standard_entry:
            return first_standard_entry.value
        return None

    @property
    def delete_requested(self) -> bool:
        deletions = getattr(self, "deletions").all()
        for deletion in deletions:
            if deletion.state == "re":
                return True
        return False

    @property
    def attributes(self) -> dict[str, Union[list[str], str]]:
        entries: dict[str, Union[list[str], str]] = {
            "Created": localtime(self.created).strftime("%d.%m.%y %H:%M"),
            "Updated": localtime(self.updated).strftime("%d.%m.%y %H:%M"),
        }
        for entry_type in self.get_unencrypted_entry_types():
            for entry in getattr(self, entry_type).all():
                entries[entry.field.name] = entry.get_value()
        return entries

    @staticmethod
    def get_unencrypted_prefetch_related():
        return [
            "state_entries",
            "state_entries__field",
            "select_entries",
            "select_entries__field",
            "standard_entries",
            "standard_entries__field",
            "users_entries",
            "users_entries__value",
            "users_entries__field",
            "multiple_entries",
            "multiple_entries__field",
            "encryptions",
            "deletions",
        ]

    def has_access(self, user: RlcUser) -> bool:
        for enc in getattr(self, "encryptions").all():
            if enc.user_id == user.id:
                return True
        return False

    def get_aes_key(self, user: Optional[RlcUser] = None, private_key_user=None):
        if user and private_key_user:
            encryption = self.encryptions.get(user=user)
            encryption.decrypt(private_key_user)
            key = encryption.key
        else:
            raise ValueError("You need to pass (user and private_key_user).")
        return key

    def get_unencrypted_entry_types(self):
        return ["state_entries", "standard_entries", "select_entries", "users_entries"]

    def get_encrypted_entry_types(self):
        return [
            "encrypted_select_entries",
            "encrypted_file_entries",
            "encrypted_standard_entries",
        ]

    def get_all_entry_types(self):
        return self.get_unencrypted_entry_types() + self.get_encrypted_entry_types()

    def get_entries(
        self, entry_types_and_serializers, aes_key_record=None, request=None, sort=False
    ):
        # this might look weird, but i've done it this way to optimize performance
        # with prefetch related
        # and watch out this expects a self from a query which has prefetched
        # all the relevant unencrypted entries otherwise the queries explode
        entries = {}
        for (entry_type, serializer) in entry_types_and_serializers:
            for entry in getattr(self, entry_type).all():
                if entry.encrypted_entry:
                    entry.decrypt(aes_key_record=aes_key_record)
                entries[entry.field.name] = serializer(
                    instance=entry, context={"request": request}
                ).data
        if sort:
            entries = dict(sorted(entries.items(), key=lambda item: item[1]["order"]))
        return entries


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
        raise NotImplementedError("This method needs to be implemented")


class RecordEntryEncryptedModelMixin(EncryptedModelMixin):
    encryption_class = AESEncryption

    # used in record for get entries
    encrypted_entry = True

    def encrypt(
        self, user: Optional[RlcUser] = None, private_key_user=None, aes_key_record=None
    ):
        record: Record = self.record  # type: ignore
        if user and private_key_user:
            key = record.get_aes_key(user=user, private_key_user=private_key_user)
        elif aes_key_record:
            key = aes_key_record
        else:
            raise ValueError(
                "You have to set (aes_key_record) or (user and private_key_user)."
            )
        super().encrypt(key)

    def decrypt(
        self, user: Optional[RlcUser] = None, private_key_user=None, aes_key_record=None
    ):
        record: Record = self.record  # type: ignore
        if user and private_key_user:
            key = record.get_aes_key(user=user, private_key_user=private_key_user)
        elif aes_key_record:
            key = aes_key_record
        else:
            raise ValueError(
                "You have to set (aes_key_record) or (user and private_key_user)."
            )
        super().decrypt(key)


class RecordStateEntry(RecordEntry):
    record = models.ForeignKey(
        Record, on_delete=models.CASCADE, related_name="state_entries"
    )
    field = models.ForeignKey(
        RecordStateField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.CharField(max_length=1000)
    closed_at = models.DateTimeField(blank=True, null=True, default=None)

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordStateEntry"
        verbose_name_plural = "RecordStateEntries"

    def __str__(self):
        return "recordStateEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        return self.value


class RecordUsersEntry(RecordEntry):
    record = models.ForeignKey(
        Record, on_delete=models.CASCADE, related_name="users_entries"
    )
    field = models.ForeignKey(
        RecordUsersField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.ManyToManyField(RlcUser, blank=True)

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordUsersEntry"
        verbose_name_plural = "RecordUsersEntries"

    def __str__(self):
        return "recordUsersEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        # this might look weird, but i've done it this way to optimize performance
        # with prefetch related
        users = []
        for user in getattr(self, "value").all():
            users.append(user.name)
        return users


class RecordSelectEntry(RecordEntry):
    record = models.ForeignKey(
        Record, on_delete=models.CASCADE, related_name="select_entries"
    )
    field = models.ForeignKey(
        RecordSelectField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.CharField(max_length=200)

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordSelectEntry"
        verbose_name_plural = "RecordSelectEntries"

    def __str__(self):
        return "recordSelectEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        return self.value


class RecordMultipleEntry(RecordEntry):
    record = models.ForeignKey(
        Record, on_delete=models.CASCADE, related_name="multiple_entries"
    )
    field = models.ForeignKey(
        RecordMultipleField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.JSONField()

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordMultipleEntry"
        verbose_name_plural = "RecordMultipleEntries"

    def __str__(self):
        return "recordMultipleEntry: {}".format(self.pk)


class RecordEncryptedSelectEntry(RecordEntryEncryptedModelMixin, RecordEntry):
    record = models.ForeignKey(
        Record, on_delete=models.CASCADE, related_name="encrypted_select_entries"
    )
    field = models.ForeignKey(
        RecordEncryptedSelectField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.BinaryField()

    # encryption
    encrypted_fields = ["value"]

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordEncryptedSelectEntry"
        verbose_name_plural = "RecordEncryptedSelectEntries"

    def __str__(self):
        return "recordEncryptedSelectEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        if self.encryption_status == "ENCRYPTED":
            self.decrypt(*args, **kwargs)
        return self.value

    def encrypt(self, *args, **kwargs):
        self.value = json.dumps(self.value)
        super().encrypt(*args, **kwargs)

    def decrypt(self, *args, **kwargs):
        super().decrypt(*args, **kwargs)
        self.value = json.loads(self.value)


class RecordEncryptedFileEntry(RecordEntry):
    record = models.ForeignKey(
        Record, on_delete=models.CASCADE, related_name="encrypted_file_entries"
    )
    field = models.ForeignKey(
        RecordEncryptedFileField, related_name="entries", on_delete=models.PROTECT
    )
    file = models.FileField(upload_to="recordmanagement/recordencryptedfileentry/")

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordEncryptedFileEntry"
        verbose_name_plural = "RecordEncryptedFileEntries"

    def __str__(self):
        return "recordEncryptedFileEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        return self.file.name.split("/")[-1].replace(".enc", "")

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)

    @staticmethod
    def encrypt_file(
        file, record, user=None, private_key_user=None, aes_key_record=None
    ):
        if user and private_key_user:
            key = record.get_aes_key(
                user=user.rlc_user, private_key_user=private_key_user
            )
        elif aes_key_record:
            key = aes_key_record
        else:
            raise ValueError(
                "You have to set (aes_key_record) or (user and private_key_user)."
            )
        name = file.name
        file = AESEncryption.encrypt_in_memory_file(file, key)
        file = DjangoFile(file, name="{}.enc".format(name))
        return file

    def decrypt_file(
        self, user: Optional[RlcUser] = None, private_key_user=None, aes_key_record=None
    ):
        if user and private_key_user:
            key = self.record.get_aes_key(user=user, private_key_user=private_key_user)
        elif aes_key_record:
            key = aes_key_record
        else:
            raise ValueError(
                "You have to set (aes_key_record) or (user and private_key_user)."
            )
        file = AESEncryption.decrypt_bytes_file(self.file, key)
        file.seek(0)
        return file


class RecordStandardEntry(RecordEntry):
    record = models.ForeignKey(
        Record, on_delete=models.CASCADE, related_name="standard_entries"
    )
    field = models.ForeignKey(
        RecordStandardField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.TextField(max_length=20000)

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordStandardEntry"
        verbose_name_plural = "RecordStandardEntries"

    def __str__(self):
        return "recordStandardEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        return self.value


class RecordEncryptedStandardEntry(RecordEntryEncryptedModelMixin, RecordEntry):
    record = models.ForeignKey(
        Record, on_delete=models.CASCADE, related_name="encrypted_standard_entries"
    )
    field = models.ForeignKey(
        RecordEncryptedStandardField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.BinaryField()

    # encryption
    encryption_class = AESEncryption
    encrypted_fields = ["value"]

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordStandardEntry"
        verbose_name_plural = "RecordStandardEntries"

    def __str__(self):
        return "recordEncryptedStandardEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        if self.encryption_status == "ENCRYPTED" or self.encryption_status is None:
            self.decrypt(*args, **kwargs)
        return self.value


class RecordStatisticEntry(RecordEntry):
    record = models.ForeignKey(
        Record, on_delete=models.CASCADE, related_name="statistic_entries"
    )
    field = models.ForeignKey(
        RecordStatisticField, related_name="entries", on_delete=models.PROTECT
    )
    value = models.CharField(max_length=200)

    class Meta:
        unique_together = ["record", "field"]
        verbose_name = "RecordStatisticEntry"
        verbose_name_plural = "RecordStatisticEntries"

    def __str__(self):
        return "recordStatisticEntry: {};".format(self.pk)

    def get_value(self, *args, **kwargs):
        return self.value


###
# RecordEncryption
###
class RecordEncryptionNew(EncryptedModelMixin, models.Model):
    user = models.ForeignKey(
        RlcUser, related_name="recordencryptions", on_delete=models.CASCADE
    )
    record = models.ForeignKey(
        Record, related_name="encryptions", on_delete=models.CASCADE
    )
    key = models.BinaryField()
    correct = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    encryption_class = RSAEncryption
    encrypted_fields = ["key"]

    class Meta:
        unique_together = ["user", "record"]
        verbose_name = "RecordEncryption"
        verbose_name_plural = "RecordEncryptions"

    def __str__(self):
        return "recordEncryption: {}; user: {}; record: {};".format(
            self.pk, self.user.email, self.record.pk
        )

    def set_correct(self, value):
        key = RecordEncryptionNew.objects.get(pk=self.pk)
        key.correct = value
        key.save()
        self.correct = value

    def test(self, private_key_user):
        try:
            super().decrypt(private_key_user)
            self.set_correct(True)
        except ValueError:
            self.set_correct(False)
            self.user.locked = True
            self.user.save()

    def decrypt(self, private_key_user=None):
        if private_key_user:
            key = private_key_user
        else:
            raise ValueError("You need to pass (private_key_user).")
        try:
            super().decrypt(key)
        except Exception as e:
            self.test(private_key_user)
            raise e

    def encrypt(self, public_key_user=None):
        if public_key_user:
            key = public_key_user
        else:
            raise ValueError("You need to pass (public_key_user).")
        super().encrypt(key)
