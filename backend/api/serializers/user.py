from backend.api.models import UserProfile
from rest_framework import serializers


class UserProfileSerializer(serializers.ModelSerializer):
    # make sure select_related('accepted') is set on the user queryset or else the queries will explode
    accepted = serializers.SerializerMethodField("get_accepted")

    class Meta:
        model = UserProfile
        exclude = ["groups", "user_permissions"]
        extra_kwargs = {"password": {"write_only": True}}

    def get_accepted(self, obj):
        return obj.get_rlc_user().accepted


class OldUserProfileSerializer(UserProfileSerializer):
    rlcgroups = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    user_has_permission = serializers.PrimaryKeyRelatedField(many=True, read_only=True)


class UserPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class UserPasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField()


class UserProfileForeignSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("id", "name", "email", "name", "phone_number")


class UserProfileNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "id",
            "name",
            'email'
        )
        extra_kwargs = {"password": {"write_only": True}}


class UserCreateProfileSerializer(UserProfileSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "password",
            "email",
            "name",
            "phone_number",
            "street",
            "city",
            "postal_code",
            "rlc",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.set_password(validated_data["password"])
        # set the default stuff
        instance.is_active = True
        instance.save()
        return instance


class UserUpdateProfileSerializer(UserProfileSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "id",
            "name",
            "phone_number",
            "street",
            "city",
            "postal_code",
            "is_active",
            "accepted",
            "email",
            "locked",
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'locked': {'read_only': True},
            'email': {'read_only': True},
        }
