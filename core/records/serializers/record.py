from typing import Optional

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.reverse import reverse

from core.records.models import (
    EncryptedClient,
    Record,
    RecordEncryptedFileEntry,
    RecordEncryptedFileField,
    RecordEncryptedSelectEntry,
    RecordEncryptedSelectField,
    RecordEncryptedStandardEntry,
    RecordEncryptedStandardField,
    RecordEncryptionNew,
    RecordMultipleEntry,
    RecordMultipleField,
    RecordSelectEntry,
    RecordSelectField,
    RecordStandardEntry,
    RecordStandardField,
    RecordStateEntry,
    RecordStateField,
    RecordStatisticEntry,
    RecordTemplate,
    RecordUpgrade,
    RecordUsersEntry,
    RecordUsersField,
)


###
# Fields
###
class RecordFieldSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    entry_url = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()  # type: ignore
    encrypted = serializers.SerializerMethodField()
    entry_view_name: Optional[str] = None
    view_name: Optional[str] = None

    def get_url(self, obj):
        return reverse(self.view_name, args=[obj.pk], request=self.context["request"])

    def get_entry_url(self, obj):
        return reverse(self.entry_view_name, request=self.context["request"])

    def get_type(self, obj):
        return obj.type

    def get_label(self, obj):
        return obj.name

    def get_kind(self, obj):
        return None

    def get_encrypted(self, obj):
        if "encrypted" in type(obj).__name__.lower():
            return "Yes"
        return "No"


class RecordStateFieldSerializer(RecordFieldSerializer):
    entry_view_name = "recordstateentry-list"
    view_name = "recordstatefield-detail"

    class Meta:
        model = RecordStateField
        fields = "__all__"

    def validate_options(self, options):
        if type(options) != list or any([type(s) is not str for s in options]):
            raise ValidationError("States need to be a list of strings.")
        if "Closed" not in options:
            raise ValidationError("Closed needs to be added to states.")
        if "Open" not in options:
            raise ValidationError("Open needs to be added to states.")
        return options

    def get_kind(self, obj):
        return "State"


class RecordSelectFieldSerializer(RecordFieldSerializer):
    entry_view_name = "recordselectentry-list"
    view_name = "recordselectfield-detail"

    class Meta:
        model = RecordSelectField
        fields = "__all__"

    def validate_options(self, options):
        if type(options) != list or any([type(o) is not str for o in options]):
            raise ValidationError("Options need to be a list of strings.")
        return options

    def get_kind(self, obj):
        return "Select"


class RecordMultipleFieldSerializer(RecordFieldSerializer):
    entry_view_name = "recordmultipleentry-list"
    view_name = "recordmultiplefield-detail"

    class Meta:
        model = RecordMultipleField
        fields = "__all__"

    def validate_options(self, options):
        if type(options) != list or any([type(o) is not str for o in options]):
            raise ValidationError("Options need to be a list of strings.")
        return options

    def get_kind(self, obj):
        return "Multiple"


class RecordEncryptedStandardFieldSerializer(RecordFieldSerializer):
    entry_view_name = "recordencryptedstandardentry-list"
    view_name = "recordencryptedstandardfield-detail"

    class Meta:
        model = RecordEncryptedStandardField
        fields = "__all__"

    def get_kind(self, obj):
        return "Encrypted Standard"


class RecordStandardFieldSerializer(RecordFieldSerializer):
    entry_view_name = "recordstandardentry-list"
    view_name = "recordstandardfield-detail"

    class Meta:
        model = RecordStandardField
        fields = "__all__"

    def get_kind(self, obj):
        return "Standard"


class RecordUsersFieldSerializer(RecordFieldSerializer):
    entry_view_name = "recordusersentry-list"
    view_name = "recordusersfield-detail"
    options = serializers.JSONField(read_only=True)

    class Meta:
        model = RecordUsersField
        fields = "__all__"

    def get_kind(self, obj):
        return "Users"


class RecordEncryptedFileFieldSerializer(RecordFieldSerializer):
    entry_view_name = "recordencryptedfileentry-list"
    view_name = "recordencryptedfilefield-detail"

    class Meta:
        model = RecordEncryptedFileField
        fields = "__all__"

    def get_kind(self, obj):
        return "Encrypted File"


class RecordEncryptedSelectFieldSerializer(RecordFieldSerializer):
    entry_view_name = "recordencryptedselectentry-list"
    view_name = "recordencryptedselectfield-detail"

    class Meta:
        model = RecordEncryptedSelectField
        fields = "__all__"

    def validate_options(self, options):
        if type(options) != list or any([type(o) is not str for o in options]):
            raise ValidationError("Options need to be a list of strings.")
        return options

    def get_kind(self, obj):
        return "Encrypted Select"


class RecordStatisticFieldSerializer(RecordFieldSerializer):
    entry_view_name = "recordstatisticentry-list"
    view_name = "recordstatisticfield-detail"

    class Meta:
        model = RecordSelectField
        fields = "__all__"

    def get_kind(self, obj):
        return "Statistic"

    def get_url(self, obj):
        return None


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

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        request = self.context.get("request", None)
        if request and getattr(request, "method", None) == "PATCH":
            fields["value"].required = True
        return fields


class RecordEncryptedFileEntrySerializer(RecordEntrySerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="recordencryptedfileentry-detail"
    )
    value = serializers.SerializerMethodField()

    class Meta:
        model = RecordEncryptedFileEntry
        fields = "__all__"

    def validate(self, attrs):
        # super
        attrs = super().validate(attrs)
        # check file was submitted
        if "file" in attrs:
            file = attrs["file"]
        else:
            raise ValidationError("A file needs to be submitted.")
        # check file size is less than 10 MB
        if file.size > 10000000:
            raise ValidationError(
                {"file": "The size of the file needs to be less than 10 MB."}
            )
        # encrypt file
        user = self.context["request"].user
        if self.instance:
            record = self.instance.record
        else:
            if "record" in attrs:
                record = attrs["record"]
            else:
                raise ValueError("A record needs to be set.")
        private_key_user = user.get_private_key(request=self.context["request"])
        attrs["file"] = RecordEncryptedFileEntry.encrypt_file(
            file, record, user=user, private_key_user=private_key_user
        )
        # return
        return attrs

    def get_value(self, obj):
        return obj.get_value()


class RecordStandardEntrySerializer(RecordEntrySerializer):
    url = serializers.HyperlinkedIdentityField(view_name="recordstandardentry-detail")

    class Meta:
        model = RecordStandardEntry
        fields = "__all__"


class RecordUsersEntrySerializer(RecordEntrySerializer):
    url = serializers.HyperlinkedIdentityField(view_name="recordusersentry-detail")

    class Meta:
        model = RecordUsersEntry
        fields = "__all__"


class RecordUsersEntryDetailSerializer(RecordUsersEntrySerializer):
    url = serializers.HyperlinkedIdentityField(view_name="recordusersentry-detail")
    value = serializers.SerializerMethodField()

    def get_value(self, obj):
        return obj.get_value()


class RecordStateEntrySerializer(RecordEntrySerializer):
    value = serializers.CharField(allow_null=False)
    url = serializers.HyperlinkedIdentityField(view_name="recordstateentry-detail")

    class Meta:
        model = RecordStateEntry
        fields = "__all__"

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance:
            field = self.instance.field
        elif "field" in attrs:
            field = attrs["field"]
        else:
            raise ValidationError("Field needs to be set.")
        if "value" in attrs and attrs["value"] not in field.options:
            raise ValidationError("The selected state is not allowed.")
        if "value" in attrs and attrs["value"] == "Closed":
            if (
                self.instance and self.instance.closed_at is None
            ) or self.instance is None:
                attrs["closed_at"] = timezone.now()
        else:
            attrs["closed_at"] = None
        return attrs


class RecordEncryptedStandardEntrySerializer(RecordEntrySerializer):
    value = serializers.CharField()
    url = serializers.HyperlinkedIdentityField(
        view_name="recordencryptedstandardentry-detail"
    )

    class Meta:
        model = RecordEncryptedStandardEntry
        fields = "__all__"

    def create(self, validated_data):
        request = self.context["request"]
        private_key_user = request.user.get_private_key(request=request)
        record = validated_data["record"]
        aes_key_record = record.get_aes_key(request.user.rlc_user, private_key_user)
        entry = RecordEncryptedStandardEntry(**validated_data)
        entry.encrypt(aes_key_record=aes_key_record)
        entry.save()
        entry.decrypt(aes_key_record=aes_key_record)
        return entry

    def update(self, instance, validated_data):
        # get the keys
        request = self.context["request"]
        private_key_user = request.user.get_private_key(request=request)
        aes_key_record = instance.record.get_aes_key(
            user=request.user.rlc_user, private_key_user=private_key_user
        )
        # update the instance
        instance.decrypt(aes_key_record=aes_key_record)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.encrypt(aes_key_record=aes_key_record)
        instance.save()
        instance.decrypt(aes_key_record=aes_key_record)
        return instance


class RecordEncryptedSelectEntrySerializer(RecordEntrySerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="recordencryptedselectentry-detail"
    )
    value = serializers.CharField()

    class Meta:
        model = RecordEncryptedSelectEntry
        fields = "__all__"

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance:
            field = self.instance.field
        elif "field" in attrs:
            field = attrs["field"]
        else:
            raise ValidationError("Field needs to be set.")
        if attrs["value"] not in set(field.options):
            raise ValidationError("The selected value is not a valid choice.")
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        private_key_user = request.user.get_private_key(request=request)
        record = validated_data["record"]
        aes_key_record = record.get_aes_key(request.user.rlc_user, private_key_user)
        entry = RecordEncryptedSelectEntry(**validated_data)
        entry.encrypt(aes_key_record=aes_key_record)
        entry.save()
        entry.decrypt(aes_key_record=aes_key_record)
        return entry

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        request = self.context["request"]
        private_key_user = request.user.get_private_key(request=request)
        aes_key_record = instance.record.get_aes_key(
            user=request.user.rlc_user, private_key_user=private_key_user
        )
        instance.encrypt(aes_key_record=aes_key_record)
        instance.save()
        instance.decrypt(aes_key_record=aes_key_record)
        return instance


class RecordSelectEntrySerializer(RecordEntrySerializer):
    url = serializers.HyperlinkedIdentityField(view_name="recordselectentry-detail")

    class Meta:
        model = RecordSelectEntry
        fields = "__all__"

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance:
            field = self.instance.field
        elif "field" in attrs:
            field = attrs["field"]
        else:
            raise ValidationError("Field needs to be set.")
        if attrs["value"] not in set(field.options):
            raise ValidationError("The selected value is not a valid choice.")
        return attrs


class RecordMultipleEntrySerializer(RecordEntrySerializer):
    url = serializers.HyperlinkedIdentityField(view_name="recordmultipleentry-detail")

    class Meta:
        model = RecordMultipleEntry
        fields = "__all__"

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance:
            field = self.instance.field
        elif "field" in attrs:
            field = attrs["field"]
        else:
            raise ValidationError("Field needs to be set.")
        if set(attrs["value"]) > set(field.options):
            raise ValidationError("The selected values contain not allowed values.")
        return attrs


class RecordStatisticEntrySerializer(RecordEntrySerializer):
    url = serializers.HyperlinkedIdentityField(view_name="recordstatisticentry-detail")

    class Meta:
        model = RecordStatisticEntry
        fields = "__all__"

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance:
            field = self.instance.field
        elif "field" in attrs:
            field = attrs["field"]
        else:
            raise ValidationError("Field needs to be set.")
        if attrs["value"] not in set(field.options):
            raise ValidationError("The selected value is not a valid choice.")
        return attrs


###
# CONSTANTS
###
FIELD_TYPES_AND_SERIALIZERS = [
    ("state_fields", RecordStateFieldSerializer),
    ("standard_fields", RecordStandardFieldSerializer),
    ("select_fields", RecordSelectFieldSerializer),
    ("multiple_fields", RecordMultipleFieldSerializer),
    ("users_fields", RecordUsersFieldSerializer),
    ("encrypted_standard_fields", RecordEncryptedStandardFieldSerializer),
    ("encrypted_select_fields", RecordEncryptedSelectFieldSerializer),
    ("encrypted_file_fields", RecordEncryptedFileFieldSerializer),
    ("statistic_fields", RecordStatisticFieldSerializer),
]


###
# Record
###
class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = "__all__"


class RecordCreateSerializer(RecordSerializer):
    pass


class ClientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(allow_blank=True)
    note = serializers.CharField(allow_blank=True)
    phone_number = serializers.CharField(allow_blank=True)

    class Meta:
        model = EncryptedClient
        exclude = ["encrypted_client_key"]


class RecordEncryptionNewSerializer(serializers.ModelSerializer):
    user_detail = serializers.SerializerMethodField()

    class Meta:
        model = RecordEncryptionNew
        fields = ["created", "user", "user_detail", "id"]

    def get_user_detail(self, obj):
        return obj.user.name


class UpgradeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    raw_folder_id = serializers.UUIDField()

    class Meta:
        model = RecordUpgrade
        fields = ["id", "raw_folder_id"]


class RecordDetailSerializer(RecordSerializer):
    entries = serializers.SerializerMethodField()
    fields = serializers.SerializerMethodField(method_name="get_form_fields")  # type: ignore
    client = serializers.SerializerMethodField()
    url = serializers.HyperlinkedIdentityField(view_name="record-detail")
    encryptions = RecordEncryptionNewSerializer(many=True)
    upgrade = UpgradeSerializer()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context["request"]
        self.user = request.user
        self.private_key_user = self.user.get_private_key(request=request)

    def get_entries(self, obj):
        try:
            aes_key_record = self.instance.get_aes_key(
                user=self.user.rlc_user, private_key_user=self.private_key_user
            )
        except ObjectDoesNotExist:
            raise PermissionDenied(
                "No encryption keys were found to decrypt this record."
            )
        entry_types_and_serializers = [
            ("state_entries", RecordStateEntrySerializer),
            ("standard_entries", RecordStandardEntrySerializer),
            ("select_entries", RecordSelectEntrySerializer),
            ("multiple_entries", RecordMultipleEntrySerializer),
            ("users_entries", RecordUsersEntrySerializer),
            ("encrypted_select_entries", RecordEncryptedSelectEntrySerializer),
            ("encrypted_file_entries", RecordEncryptedFileEntrySerializer),
            ("encrypted_standard_entries", RecordEncryptedStandardEntrySerializer),
            ("statistic_entries", RecordStatisticEntrySerializer),
        ]
        return obj.get_entries(
            entry_types_and_serializers,
            aes_key_record=aes_key_record,
            request=self.context["request"],
            sort=True,
        )

    def get_form_fields(self, obj):
        return obj.template.get_fields(
            FIELD_TYPES_AND_SERIALIZERS, request=self.context["request"]
        )

    def get_client(self, obj):
        if obj.old_client is None:
            return {}
        private_key_rlc = self.user.rlc.get_private_key(
            user=self.user, private_key_user=self.private_key_user
        )
        obj.old_client.decrypt(private_key_rlc=private_key_rlc)
        return ClientSerializer(instance=obj.old_client).data


###
# RecordTemplate
###
class RecordTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordTemplate
        fields = "__all__"

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["rlc"] = self.context["request"].user.rlc
        return attrs

    def validate_show(self, val):
        if self.instance:
            field_types_and_serializer = [
                ("state_fields", RecordStateFieldSerializer),
                ("standard_fields", RecordStandardFieldSerializer),
                ("select_fields", RecordSelectFieldSerializer),
                ("multiple_fields", RecordMultipleFieldSerializer),
                ("users_fields", RecordUsersFieldSerializer),
            ]
            fields = self.instance.get_fields(
                field_types_and_serializer, request=self.context["request"]
            )
            possible_names = list(map(lambda f: f["name"], fields))
            possible_names.append("Created")
            possible_names.append("Updated")
            for name in val:
                if name not in possible_names:
                    raise ValidationError(
                        "The value '{}' is not contained within the possible fields. "
                        "Please check upper or lower case and whitespaces.\n"
                        "Possible fields: \n{}".format(name, possible_names)
                    )
        else:
            val = []
        return val


class RecordTemplateDetailSerializer(RecordTemplateSerializer):
    fields = serializers.SerializerMethodField(method_name="get_form_fields")  # type: ignore

    def get_form_fields(self, obj):
        return obj.get_fields(
            FIELD_TYPES_AND_SERIALIZERS, request=self.context["request"]
        )
