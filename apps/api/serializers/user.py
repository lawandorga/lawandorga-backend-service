from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.serializers import AuthTokenSerializer as DRFAuthTokenSerializer
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import update_last_login
from rest_framework.exceptions import ValidationError, ParseError
from apps.api.serializers.rlc import RlcSerializer
from django.contrib.auth import authenticate
from apps.api.models import UserProfile, RlcUser
from rest_framework import serializers
from django.db import transaction


###
# RlcUser
###
class RlcUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')
    email = serializers.SerializerMethodField('get_email')

    class Meta:
        model = RlcUser
        fields = '__all__'

    def get_name(self, obj):
        return obj.user.name

    def get_email(self, obj):
        return obj.user.email


class RlcUserUpdateSerializer(RlcUserSerializer):
    name = serializers.CharField(required=True)

    class Meta:
        model = RlcUser
        fields = ['name', 'phone_number', 'birthday', 'street', 'city', 'postal_code', 'is_active', 'note']

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if (
            'is_active' in attrs and
            self.instance.pk == self.context['request'].user.rlc_user.pk and
            attrs['is_active'] is False
        ):
            raise ParseError('You can not deactivate yourself.')
        return attrs

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if 'name' in validated_data:
            instance.user.name = validated_data['name']
            instance.user.save()
        return instance


class RlcUserForeignSerializer(RlcUserSerializer):
    class Meta:
        model = RlcUser
        fields = ("user", "id", "phone_number", 'name', 'email', 'note')


###
# UserProfile
###
class UserProfileSerializer(serializers.ModelSerializer):
    rlcuserid = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        exclude = ["groups", "user_permissions"]
        extra_kwargs = {"password": {"write_only": True}}

    def get_rlcuserid(self, obj):
        return obj.rlc_user.id


class UserProfileChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()
    new_password_confirm = serializers.CharField()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise ValidationError('The two new passwords are not equal.')
        return attrs

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError('The password is not correct.')
        return value


class UserProfileSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['name', 'id']


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
    new_password_confirm = serializers.CharField()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise ValidationError('The passwords do not match.')
        return attrs


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
            # apps.)
            if not user:
                msg = "This email doesn't exist or the password is wrong."
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Please enter your email and your password.'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


###
# JWT
###
class JWTSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    def get_token(self, user):
        token = super().get_token(user)
        password_user = self.initial_data['password']
        token['key'] = user.get_private_key(password_user=password_user)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        # data['user'] = RlcUserSerializer(self.user.rlc_user).data
        data['user'] = RlcUserSerializer(self.user.rlc_user).data
        data['rlc'] = RlcSerializer(self.user.rlc).data
        data['permissions'] = self.user.get_all_user_permissions()

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data
