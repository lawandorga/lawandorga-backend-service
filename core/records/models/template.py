from django.apps import apps
from django.db import models
from django.urls import reverse

from core.models import Group, Org


###
# RecordTemplate
###
def get_default_show():
    return ["Token", "State", "Consultants", "Tags", "Official Note"]


class RecordTemplate(models.Model):
    @classmethod
    def create(cls, name: str, org: Org, pk=0) -> "RecordTemplate":
        template = RecordTemplate(name=name, rlc=org)
        if pk:
            template.pk = pk
        return template

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
            "statistic_fields",
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

    def get_fields_new(self):
        fields = []
        for field_type in self.get_field_types():
            for field in getattr(self, field_type).all():
                data = {
                    "entry_url": field.entry_url,
                    "label": field.name,
                    "name": field.name,
                    "type": field.type,
                    "kind": field.kind,
                    "id": field.pk,
                    "order": field.order,
                }
                if hasattr(field, "options"):
                    data["options"] = field.options
                fields.append(data)
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
    entry_view_name: str

    class Meta:
        abstract = True

    @property
    def type(self):
        raise NotImplementedError("This property needs to be implemented.")

    @property
    def entry_url(self):
        url = reverse(self.entry_view_name)
        return url

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
    entry_view_name = "recordstateentry-list"

    class Meta:
        verbose_name = "RecordStateField"
        verbose_name_plural = "RecordStateFields"

    @property
    def type(self):
        return "select"

    @property
    def kind(self):
        return "State"

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
    entry_view_name = "recordusersentry-list"

    class Meta:
        verbose_name = "RecordUsersField"
        verbose_name_plural = "RecordUsersFields"

    @property
    def kind(self):
        return "Users"

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
    entry_view_name = "recordselectentry-list"

    class Meta:
        verbose_name = "RecordSelectField"
        verbose_name_plural = "RecordSelectFields"

    @property
    def type(self):
        return "select"

    @property
    def kind(self):
        return "Select"

    def __str__(self):
        return "recordSelectField: {}; name: {};".format(self.pk, self.name)


class RecordMultipleField(RecordField):
    template = models.ForeignKey(
        RecordTemplate, on_delete=models.CASCADE, related_name="multiple_fields"
    )
    options = models.JSONField(default=list)
    entry_view_name = "recordmultipleentry-list"

    class Meta:
        verbose_name = "RecordMultipleField"
        verbose_name_plural = "RecordMultipleFields"

    @property
    def type(self):
        return "multiple"

    @property
    def kind(self):
        return "Multiple"

    def __str__(self):
        return "recordMultipleField: {}; name: {};".format(self.pk, self.name)


class RecordEncryptedSelectField(RecordField):
    template = models.ForeignKey(
        RecordTemplate, on_delete=models.CASCADE, related_name="encrypted_select_fields"
    )
    options = models.JSONField(default=list)
    entry_view_name = "recordencryptedselectentry-list"

    class Meta:
        verbose_name = "RecordEncryptedSelectField"
        verbose_name_plural = "RecordEncryptedSelectFields"

    @property
    def type(self):
        return "select"

    @property
    def kind(self):
        return "Encrypted Select"

    def __str__(self):
        return "recordEncryptedSelectField: {}; name: {};".format(self.pk, self.name)


class RecordEncryptedFileField(RecordField):
    template = models.ForeignKey(
        RecordTemplate, on_delete=models.CASCADE, related_name="encrypted_file_fields"
    )
    entry_view_name = "recordencryptedfileentry-list"

    class Meta:
        verbose_name = "RecordEncryptedFileField"
        verbose_name_plural = "RecordEncryptedFileFields"

    @property
    def type(self):
        return "file"

    @property
    def kind(self):
        return "Encrypted File"

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
    entry_view_name = "recordstandardentry-list"

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
    entry_view_name = "recordencryptedstandardentry-list"

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


class RecordStatisticField(RecordField):
    template = models.ForeignKey(
        RecordTemplate, on_delete=models.CASCADE, related_name="statistic_fields"
    )
    options = models.JSONField(default=list)
    helptext = models.CharField(max_length=1000)
    entry_view_name = "recordstatisticentry-list"

    class Meta:
        verbose_name = "RecordStatisticField"
        verbose_name_plural = "RecordStatisticFields"

    @property
    def type(self):
        return "select"

    @property
    def kind(self):
        return "Statistic"

    def __str__(self):
        return "recordStatisticField: {}; name: {};".format(self.pk, self.name)
