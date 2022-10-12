from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.core.models import UserProfile


###
# Password
###
class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()
    new_password_confirm = serializers.CharField()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise ValidationError("The two new passwords are not equal.")
        return attrs

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise ValidationError("The password is not correct.")
        return value


###
# Other
###
class UserProfileSerializer(serializers.ModelSerializer):
    rlcuserid = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        exclude = ["groups", "user_permissions"]
        extra_kwargs = {"password": {"write_only": True}}

    def get_rlcuserid(self, obj):
        return obj.rlc_user.id
