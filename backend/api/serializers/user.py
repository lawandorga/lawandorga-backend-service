from rest_framework.authtoken.serializers import AuthTokenSerializer as DRFAuthTokenSerializer
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate
from backend.api.models import UserProfile, RlcUser
from rest_framework import serializers
from django.db import transaction


###
# RlcUser
###
class RlcUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RlcUser
        fields = '__all__'


class RlcUserListSerializer(RlcUserSerializer):
    name = serializers.SerializerMethodField('get_name')
    email = serializers.SerializerMethodField('get_email')

    def get_name(self, obj):
        return obj.user.name

    def get_email(self, obj):
        return obj.user.email


class RlcUserUpdateSerializer(RlcUserSerializer):
    name = serializers.CharField(required=True)

    class Meta:
        model = RlcUser
        fields = ['name', 'phone_number', 'birthday', 'street', 'city', 'postal_code']

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.user.name = validated_data['name']
        instance.user.save()
        return instance


class RlcUserForeignSerializer(serializers.ModelSerializer):
    class Meta:
        model = RlcUser
        fields = ("user", "id", "name", "email", "name", "phone_number")


###
# UserProfile
###
class UserProfileSerializer(serializers.ModelSerializer):
    # make sure select_related('accepted') is set on the user queryset or else the queries will explode
    accepted = serializers.SerializerMethodField("get_accepted")

    class Meta:
        model = UserProfile
        exclude = ["groups", "user_permissions"]
        extra_kwargs = {"password": {"write_only": True}}

    def get_accepted(self, obj):
        return obj.get_rlc_user().accepted


class RlcUserCreateSerializer(UserProfileSerializer):
    password_confirm = serializers.CharField(write_only=True)

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
        if attrs['password'] != attrs['password_confirm']:
            raise ValidationError('Both passwords must be equal.')
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password_confirm')
        user = UserProfile(**validated_data)
        user.set_password(password)
        with transaction.atomic():
            user.save()
            rlc_user = RlcUser(user=user, email_confirmed=False)
            rlc_user.save()
            rlc_user.send_email_confirmation_email()
        return user


class UserProfileNameSerializer(UserProfileSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "id",
            'rlc_user',
            "name",
            'email'
        )


###
# Other
###
class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class UserPasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField()


###
# Token
###
class AuthTokenSerializer(DRFAuthTokenSerializer):
    username = None
    email = serializers.CharField(label="E-Mail")

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                username=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = "This email doesn't exist or the password is wrong."
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Please enter your email and your password.'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
