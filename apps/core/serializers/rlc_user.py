from smtplib import SMTPRecipientsRefused

from django.contrib.auth.models import update_last_login
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings

from apps.core.models import Org, RlcUser, UserProfile
from apps.core.serializers import RlcSerializer
from config.authentication import RefreshPrivateKeyToken


###
# UserProfile
###
class RlcUserCreateSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    rlc = serializers.PrimaryKeyRelatedField(queryset=Org.objects.all(), required=True)

    class Meta:
        model = UserProfile
        fields = [
            "password",
            "password_confirm",
            "email",
            "name",
            "rlc",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise ValidationError("Both passwords must be equal.")
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password_confirm")
        user = UserProfile(**validated_data)
        user.set_password(password)
        with transaction.atomic():
            user.save()
            rlc_user = RlcUser(user=user, email_confirmed=False)
            rlc_user.save()
        try:
            rlc_user.send_email_confirmation_email()
        except SMTPRecipientsRefused:
            user.delete()
            raise ValidationError(
                {
                    "email": [
                        "We could not send a confirmation email to this address. "
                        "Please check if this email is correct."
                    ]
                }
            )
        return user


###
# RlcUser
###
class RlcUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField("get_name")
    email = serializers.SerializerMethodField("get_email")
    speciality_of_study_display = serializers.SerializerMethodField("get_study")

    class Meta:
        model = RlcUser
        exclude = ["private_key", "public_key", "is_private_key_encrypted"]

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


###
# JWT
###
class RlcUserJWTSerializer(TokenObtainSerializer):
    token_class = RefreshPrivateKeyToken

    def get_token(self, user):
        return self.token_class.for_user(
            user, password_user=self.initial_data["password"]
        )

    def validate(self, attrs):
        data = super().validate(attrs)

        if not hasattr(self.user, "rlc_user"):
            raise ValidationError(
                "You don't have the necessary role to be able to login here."
            )

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        data["user"] = RlcUserSerializer(self.user.rlc_user).data
        data["rlc"] = RlcSerializer(self.user.rlc).data
        data["permissions"] = self.user.get_all_user_permissions()

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data


###
# Other
###
class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class UserPasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField()
    new_password_confirm = serializers.CharField()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise ValidationError("The passwords do not match.")
        return attrs
