from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import update_last_login
from rest_framework.exceptions import ValidationError
from apps.api.models import StatisticUser
from rest_framework import serializers


###
# StatisticUser
###
class StatisticUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')
    email = serializers.SerializerMethodField('get_email')

    class Meta:
        model = StatisticUser
        fields = '__all__'

    def get_name(self, obj):
        return obj.user.name

    def get_email(self, obj):
        return obj.user.email


###
# JWT
###
class StatisticUserJWTSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    def validate(self, attrs):
        data = super().validate(attrs)

        if not hasattr(self.user, 'statistic_user'):
            raise ValidationError("You don't have the necessary role to be able to login here.")

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        data['user'] = StatisticUserSerializer(self.user.statistic_user).data

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data
