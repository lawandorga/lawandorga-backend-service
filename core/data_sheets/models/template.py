from typing import TYPE_CHECKING, cast
from uuid import uuid4

from django.apps import apps
from django.core.files.uploadedfile import UploadedFile
from django.db import models, transaction
from django.utils import timezone

from core.auth.models.org_user import RlcUser
from core.folders.domain.repositiories.folder import FolderRepository
from core.models import Group, Org
from core.seedwork.domain_layer import DomainError
from core.seedwork.repository import RepositoryWarehouse

if TYPE_CHECKING:
    from .data_sheet import (
        DataSheet,
        DataSheetEncryptedFileEntry,
        DataSheetEncryptedSelectEntry,
        DataSheetEncryptedStandardEntry,
        DataSheetMultipleEntry,
        DataSheetSelectEntry,
        DataSheetStandardEntry,
        DataSheetStateEntry,
        DataSheetStatisticEntry,
        DataSheetUsersEntry,
    )


###
# RecordTemplate
###
class DataSheetTemplate(models.Model):
    @classmethod
    def create(cls, name: str, org: Org, pk=0) -> "DataSheetTemplate":
        template = DataSheetTemplate(name=name, rlc=org)
        if pk:
            template.pk = pk
        return template

    name = models.CharField(max_length=200)
    rlc = models.ForeignKey(
        Org, related_name="recordtemplates", on_delete=models.CASCADE, blank=True
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        rlc_id: int
        records: models.QuerySet[DataSheet]
        state_fields: models.QuerySet["DataSheetStateField"]
        standard_fields: models.QuerySet["DataSheetStandardField"]
        select_fields: models.QuerySet["DataSheetSelectField"]
        multiple_fields: models.QuerySet["DataSheetMultipleField"]
        users_fields: models.QuerySet["DataSheetUsersField"]

    class Meta:
        verbose_name = "RecordTemplate"
        verbose_name_plural = "RecordTemplates"

    def __str__(self):
        return "recordTemplate: {}; rlc: {};".format(self.pk, self.rlc)

    @property
    def show_options(self):
        fields = [
            *list(self.state_fields.all()),
            *list(self.standard_fields.all()),
            *list(self.select_fields.all()),
            *list(self.multiple_fields.all()),
            *list(self.users_fields.all()),
        ]
        possible_names = list(map(lambda f: f.name, fields))
        possible_names.append("Created")
        possible_names.append("Updated")
        possible_names.append("Name")
        return possible_names

    @property
    def fields(self):
        fields = []
        for field in self.get_field_types():
            fields += list(getattr(self, field).all())
        fields = list(sorted(fields, key=lambda i: i.order))
        return fields

    def get_field_types(self):
        return [
            "standard_fields",
            "state_fields",
            "users_fields",
            "select_fields",
            "multiple_fields",
            "statistic_fields",
            "encrypted_standard_fields",
            "encrypted_select_fields",
            "encrypted_file_fields",
        ]

    def update_name(self, name: str):
        self.name = name

    def update_show(self, show: list[str]):
        possible = self.show_options
        for name in show:
            if name not in possible:
                raise DomainError(
                    "The field name '{}' is not allowed.\n\nPossible names are: '{}'.".format(
                        name, ", ".join(possible)
                    )
                )
        self.show = show

    def get_fields_new(self):
        fields = []
        for field_type in self.get_field_types():
            for field in getattr(self, field_type).all():
                data = {
                    "label": field.name,
                    "name": field.name,
                    "type": field.type,
                    "kind": field.kind,
                    "id": field.pk,
                    "uuid": field.uuid,
                    "order": field.order,
                }
                if hasattr(field, "options"):
                    data["options"] = field.options
                fields.append(data)
        fields = list(sorted(fields, key=lambda i: i["order"]))
        return fields

    @classmethod
    def get_statistic_fields_meta(cls):
        from core.data_sheets.fixtures import get_all_countries

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
            if not DataSheetStatisticField.objects.filter(
                name=field["name"], template=self
            ).exists():
                DataSheetStatisticField.objects.create(template=self, **field)


###
# RecordField
###
class RecordField(models.Model):
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    name = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @property
    def type(self):
        raise NotImplementedError("This property needs to be implemented.")

    @property
    def encrypted(self):
        if "Encrypted" in self.__class__.__name__:
            return "Yes"
        return "No"

    @classmethod
    def get_entry_model(cls):
        name = cls.__name__.replace("Field", "Entry")
        model = apps.get_model("core", name)
        return model

    def create_entry(self, user: RlcUser, record_id: int, value: str | list[str]):
        raise NotImplementedError()

    def update_entry(self, user: RlcUser, record_id: int, value: str | list[str]):
        raise NotImplementedError()

    def delete_entry(self, record_id: int):
        raise NotImplementedError()


class DataSheetStateField(RecordField):
    template = models.ForeignKey(
        DataSheetTemplate, on_delete=models.CASCADE, related_name="state_fields"
    )
    options = models.JSONField(default=list)

    if TYPE_CHECKING:
        entries: models.QuerySet["DataSheetStateEntry"]

    class Meta:
        verbose_name = "RecordStateField"
        verbose_name_plural = "RecordStateFields"

    @property
    def field_type(self):
        return self.type

    @property
    def type(self):
        return "select"

    @property
    def kind(self):
        return "State"

    def __str__(self):
        return "recordStateField: {}; name: {};".format(self.pk, self.name)

    def validate_value(self, value: str):
        if value not in self.options:
            raise DomainError(
                "The value is not in the options: {}.".format(self.options)
            )

    def create_entry(self, user: RlcUser, record_id: int, value: str | list[str]):
        from .data_sheet import DataSheetStateEntry

        assert isinstance(value, str)
        self.validate_value(value)
        entry = DataSheetStateEntry(field_id=self.pk, record_id=record_id, value=value)
        if value == "Closed":
            entry.closed_at = timezone.now()
        entry.save()

    def update_entry(self, user: RlcUser, record_id: int, value: str | list[str]):
        assert isinstance(value, str)
        self.validate_value(value)
        entry = self.entries.get(record_id=record_id)
        if entry.value != "Closed" and value == "Closed":
            entry.closed_at = timezone.now()
        entry.value = value
        entry.save()

    def delete_entry(self, record_id: int):
        self.entries.get(record_id=record_id).delete()


class DataSheetUsersField(RecordField):
    template = models.ForeignKey(
        DataSheetTemplate, on_delete=models.CASCADE, related_name="users_fields"
    )
    share_keys = models.BooleanField(default=True)
    group = models.ForeignKey(
        Group, blank=True, null=True, default=None, on_delete=models.SET_NULL
    )

    if TYPE_CHECKING:
        entries: models.QuerySet["DataSheetUsersEntry"]

    class Meta:
        verbose_name = "RecordUsersField"
        verbose_name_plural = "RecordUsersFields"

    @property
    def kind(self):
        return "Users"

    @property
    def field_type(self):
        return self.type

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

    def create_entry(self, user: RlcUser, record_id: int, value: str | list[str]):
        from .data_sheet import DataSheetUsersEntry

        assert isinstance(value, list)
        entry = DataSheetUsersEntry(field_id=self.pk, record_id=record_id)
        with transaction.atomic():
            entry.save()
            entry.value.set(value)  # type: ignore
        self.do_share_keys(user, entry)

    def do_share_keys(self, user: RlcUser, entry: "DataSheetUsersEntry"):
        if self.share_keys:
            record = entry.record
            assert record.folder_uuid is not None
            r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
            folder = r.retrieve(user.org_id, record.folder_uuid)
            for u in list(entry.value.all()):
                if not folder.has_access(u):
                    folder.grant_access(u, user)
            r.save(folder)

    def update_entry(self, user: RlcUser, record_id: int, value: str | list[str]):
        entry = self.entries.get(record_id=record_id)
        entry.value.set(value)  # type: ignore
        self.do_share_keys(user, entry)

    def delete_entry(self, record_id: int):
        self.entries.get(record_id=record_id).delete()


class DataSheetSelectField(RecordField):
    template = models.ForeignKey(
        DataSheetTemplate, on_delete=models.CASCADE, related_name="select_fields"
    )
    options = models.JSONField(default=list)

    if TYPE_CHECKING:
        entries: models.QuerySet["DataSheetSelectEntry"]

    class Meta:
        verbose_name = "RecordSelectField"
        verbose_name_plural = "RecordSelectFields"

    @property
    def field_type(self):
        return self.type

    @property
    def type(self):
        return "select"

    @property
    def kind(self):
        return "Select"

    def __str__(self):
        return "recordSelectField: {}; name: {};".format(self.pk, self.name)

    def validate_value(self, value: str | list[str]):
        assert isinstance(value, str)
        if value not in self.options:
            raise DomainError(
                "The value is not in the options: {}.".format(self.options)
            )

    def create_entry(self, user: RlcUser, record_id: int, value: str | list[str]):
        from .data_sheet import DataSheetSelectEntry

        self.validate_value(value)
        assert isinstance(value, str)
        entry = DataSheetSelectEntry(field_id=self.pk, record_id=record_id, value=value)
        entry.save()

    def update_entry(self, user: RlcUser, record_id: int, value: str | list[str]):
        self.validate_value(value)
        entry = self.entries.get(record_id=record_id)
        assert isinstance(value, str)
        entry.value = value
        entry.save()

    def delete_entry(self, record_id: int):
        self.entries.get(record_id=record_id).delete()


class DataSheetMultipleField(RecordField):
    template = models.ForeignKey(
        DataSheetTemplate, on_delete=models.CASCADE, related_name="multiple_fields"
    )
    options = models.JSONField(default=list)

    if TYPE_CHECKING:
        entries: models.QuerySet["DataSheetMultipleEntry"]

    class Meta:
        verbose_name = "RecordMultipleField"
        verbose_name_plural = "RecordMultipleFields"

    @property
    def field_type(self):
        return self.type

    @property
    def type(self):
        return "multiple"

    @property
    def kind(self):
        return "Multiple"

    def __str__(self):
        return "recordMultipleField: {}; name: {};".format(self.pk, self.name)

    def validate_value(self, value: str | list[str]):
        assert isinstance(value, list)
        if not all([i in self.options for i in value]):
            raise DomainError(
                "The value is not in the options: {}.".format(self.options)
            )

    def create_entry(self, user: RlcUser, record_id: int, value: str | list[str]):
        from .data_sheet import DataSheetMultipleEntry

        self.validate_value(value)
        entry = DataSheetMultipleEntry(
            field_id=self.pk, record_id=record_id, value=value
        )
        entry.save()

    def update_entry(self, user: RlcUser, record_id: int, value: str | list[str]):
        self.validate_value(value)
        entry = self.entries.get(record_id=record_id)
        entry.value = value
        entry.save()

    def delete_entry(self, record_id: int):
        self.entries.get(record_id=record_id).delete()


class DataSheetEncryptedSelectField(RecordField):
    template = models.ForeignKey(
        DataSheetTemplate,
        on_delete=models.CASCADE,
        related_name="encrypted_select_fields",
    )
    options = models.JSONField(default=list)

    if TYPE_CHECKING:
        entries: models.QuerySet["DataSheetEncryptedSelectEntry"]

    class Meta:
        verbose_name = "RecordEncryptedSelectField"
        verbose_name_plural = "RecordEncryptedSelectFields"

    @property
    def field_type(self):
        return self.type

    @property
    def type(self):
        return "select"

    @property
    def kind(self):
        return "Encrypted Select"

    def __str__(self):
        return "recordEncryptedSelectField: {}; name: {};".format(self.pk, self.name)

    def validate_value(self, value: str | list[str]):
        assert isinstance(value, str)
        if value not in self.options:
            raise DomainError(
                "The value is not in the options: {}.".format(self.options)
            )

    def create_entry(self, user: RlcUser, record_id: int, value: str | list[str]):
        from .data_sheet import DataSheetEncryptedSelectEntry

        self.validate_value(value)
        entry = DataSheetEncryptedSelectEntry(
            field_id=self.pk, record_id=record_id, value=value
        )
        entry.encrypt(user=user)
        entry.save()

    def update_entry(self, user: RlcUser, record_id: int, value: str | list[str]):
        self.validate_value(value)
        entry = self.entries.get(record_id=record_id)
        entry.value = value  # type: ignore
        entry.encrypt(user=user)
        entry.save()

    def delete_entry(self, record_id: int):
        self.entries.get(record_id=record_id).delete()


class DataSheetEncryptedFileField(RecordField):
    template = models.ForeignKey(
        DataSheetTemplate,
        on_delete=models.CASCADE,
        related_name="encrypted_file_fields",
    )

    view_name = "recordencryptedfilefield-list"

    if TYPE_CHECKING:
        entries: models.QuerySet["DataSheetEncryptedFileEntry"]

    class Meta:
        verbose_name = "RecordEncryptedFileField"
        verbose_name_plural = "RecordEncryptedFileFields"

    @property
    def field_type(self):
        return self.type

    @property
    def type(self):
        return "file"

    @property
    def kind(self):
        return "Encrypted File"

    def __str__(self):
        return "recordEncryptedFileField: {}; name: {};".format(self.pk, self.name)

    def create_entry(self, user: RlcUser, record_id: int, value: str | list[str]):
        raise Exception("this is not supported")

    def update_entry(self, user: RlcUser, record_id: int, value: str | list[str]):
        raise Exception("this is not supported")

    def upload_file(self, user: RlcUser, record_id: int, file: UploadedFile) -> None:
        from .data_sheet import DataSheetEncryptedFileEntry

        if file.size and file.size > 10000000:
            raise DomainError("The size of the file needs to be less than 10 MB.")

        private_key_user = user.get_private_key()
        record = self.template.records.get(id=record_id)
        enc_file = DataSheetEncryptedFileEntry.encrypt_file(
            file, record, user=user, private_key_user=private_key_user
        )
        entry = DataSheetEncryptedFileEntry(record_id=record_id, field_id=self.pk)
        entry.save()
        entry.file.save(file.name, enc_file)

    def delete_entry(self, record_id: int):
        self.entries.get(record_id=record_id).delete()


class DataSheetStandardField(RecordField):
    template = models.ForeignKey(
        DataSheetTemplate, on_delete=models.CASCADE, related_name="standard_fields"
    )
    TYPE_CHOICES = (
        ("TEXTAREA", "Multi Line"),
        ("TEXT", "Single Line"),
        ("DATETIME-LOCAL", "Date and Time"),
        ("DATE", "Date"),
    )
    field_type = models.CharField(choices=TYPE_CHOICES, max_length=20, default="TEXT")

    if TYPE_CHECKING:
        entries: models.QuerySet["DataSheetStandardEntry"]

    class Meta:
        verbose_name = "RecordStandardField"
        verbose_name_plural = "RecordStandardFields"

    @property
    def type(self):
        return self.field_type.lower()

    @property
    def kind(self):
        return "Standard"

    def __str__(self):
        return "recordStandardField: {}; name: {};".format(self.pk, self.name)

    @staticmethod
    def get_field_types():
        return [
            "state_fields",
            "standard_fields",
            "select_fields",
            "multiple_fields",
            "users_fields",
            "encrypted_standard_fields",
            "encrypted_select_fields",
            "encrypted_file_fields",
            "statistic_fields",
        ]

    def validate_value(self, value: str | list[str]):
        assert isinstance(value, str)

    def create_entry(self, user: RlcUser, record_id: int, value: str | list[str]):
        from .data_sheet import DataSheetStandardEntry

        self.validate_value(value)
        assert isinstance(value, str)
        entry = DataSheetStandardEntry(
            field_id=self.pk, record_id=record_id, value=value
        )
        entry.save()

    def update_entry(self, user: RlcUser, record_id: int, value: str | list[str]):
        self.validate_value(value)
        entry = self.entries.get(record_id=record_id)
        assert isinstance(value, str)
        entry.value = value
        entry.save()

    def delete_entry(self, record_id: int):
        self.entries.get(record_id=record_id).delete()


class DataSheetEncryptedStandardField(RecordField):
    template = models.ForeignKey(
        DataSheetTemplate,
        on_delete=models.CASCADE,
        related_name="encrypted_standard_fields",
    )
    TYPE_CHOICES = (
        ("TEXTAREA", "Multi Line"),
        ("TEXT", "Single Line"),
        ("DATE", "Date"),
    )
    field_type = models.CharField(choices=TYPE_CHOICES, max_length=20, default="TEXT")

    if TYPE_CHECKING:
        entries: models.QuerySet["DataSheetEncryptedStandardEntry"]

    class Meta:
        verbose_name = "RecordEncryptedStandardField"
        verbose_name_plural = "RecordEncryptedStandardFields"

    @property
    def type(self):
        return self.field_type.lower()

    @property
    def kind(self):
        return "Encrypted Standard"

    def __str__(self):
        return "recordEncryptedStandardField: {}; name: {};".format(self.pk, self.name)

    def validate_value(self, value: str | list[str]):
        assert isinstance(value, str)

    def create_entry(self, user: RlcUser, record_id: int, value: str | list[str]):
        from .data_sheet import DataSheetEncryptedStandardEntry

        self.validate_value(value)
        entry = DataSheetEncryptedStandardEntry(
            field_id=self.pk, record_id=record_id, value=value
        )
        entry.encrypt(user=user)
        entry.save()

    def update_entry(self, user: RlcUser, record_id: int, value: str | list[str]):
        self.validate_value(value)
        entry = self.entries.get(record_id=record_id)
        entry.value = value  # type: ignore
        entry.encrypt(user)
        entry.save()

    def delete_entry(self, record_id: int):
        self.entries.get(record_id=record_id).delete()


class DataSheetStatisticField(RecordField):
    template = models.ForeignKey(
        DataSheetTemplate, on_delete=models.CASCADE, related_name="statistic_fields"
    )
    options = models.JSONField(default=list)
    helptext = models.CharField(max_length=1000)

    if TYPE_CHECKING:
        entries: models.QuerySet["DataSheetStatisticEntry"]

    class Meta:
        verbose_name = "RecordStatisticField"
        verbose_name_plural = "RecordStatisticFields"

    @property
    def field_type(self):
        return self.type

    @property
    def type(self):
        return "select"

    @property
    def kind(self):
        return "Statistic"

    def __str__(self):
        return "recordStatisticField: {}; name: {};".format(self.pk, self.name)

    def validate_value(self, value: str | list[str]):
        assert isinstance(value, str)

    def create_entry(self, user: RlcUser, record_id: int, value: str | list[str]):
        from .data_sheet import DataSheetStatisticEntry

        self.validate_value(value)
        assert isinstance(value, str)
        entry = DataSheetStatisticEntry(
            record_id=record_id, field_id=self.pk, value=value
        )
        entry.save()

    def update_entry(self, user: RlcUser, record_id: int, value: str | list[str]):
        self.validate_value(value)
        entry = self.entries.get(record_id=record_id)
        assert isinstance(value, str)
        entry.value = value
        entry.save()

    def delete_entry(self, record_id: int):
        self.entries.get(record_id=record_id).delete()
