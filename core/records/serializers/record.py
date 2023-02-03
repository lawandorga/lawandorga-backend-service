from typing import Optional

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from core.records.models import (
    RecordEncryptedFileEntry,
    RecordEncryptedFileField,
    RecordEncryptedSelectEntry,
    RecordEncryptedSelectField,
    RecordEncryptedStandardEntry,
    RecordEncryptedStandardField,
    RecordMultipleEntry,
    RecordMultipleField,
    RecordSelectEntry,
    RecordSelectField,
    RecordStandardEntry,
    RecordStandardField,
    RecordStateEntry,
    RecordStateField,
    RecordStatisticEntry,
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

    def validate_name(self, val: str):
        if val == "Name":
            raise ValidationError("You are not allowed to use 'Name' as field name.")
        return val


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
    entry_view_name = "recordmultipleentry-list"
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
        if not (set(attrs["value"]) <= set(field.options)):
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
