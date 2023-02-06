from rest_framework import serializers
from rest_framework.exceptions import ParseError

from core.models import RlcUser


class RlcUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField("get_name")
    email = serializers.SerializerMethodField("get_email")
    speciality_of_study_display = serializers.SerializerMethodField("get_study")

    class Meta:
        model = RlcUser
        exclude = [
            "old_private_key",
            "old_public_key",
            "is_private_key_encrypted",
            "key",
        ]

    def get_name(self, obj):
        return obj.user.name

    def get_email(self, obj):
        return obj.user.email

    def get_study(self, obj):
        return obj.get_speciality_of_study_display()


class RlcUserUpdateSerializer(RlcUserSerializer):
    class Meta:
        model = RlcUser
        fields = [
            "name",
            "phone_number",
            "birthday",
            "street",
            "city",
            "postal_code",
            "is_active",
            "note",
            "speciality_of_study",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if (
            "is_active" in attrs
            and self.instance.pk == self.context["request"].user.rlc_user.pk
            and attrs["is_active"] is False
        ):
            raise ParseError("You can not deactivate yourself.")
        return attrs

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if "name" in validated_data:
            instance.user.name = validated_data["name"]
            instance.user.save()
        return instance


class RlcUserForeignSerializer(RlcUserSerializer):
    class Meta:
        model = RlcUser
        fields = [
            "user",
            "id",
            "phone_number",
            "name",
            "email",
            "accepted",
            "email_confirmed",
            "locked",
            "is_active",
        ]
