#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>
from django.core.exceptions import ObjectDoesNotExist

from backend.api.models import UserProfile
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    # make sure select_related('accepted') is set on the user queryset or else the queries will explode
    accepted = serializers.SerializerMethodField("get_accepted")

    class Meta:
        model = UserProfile
        exclude = ["groups", "user_permissions"]
        extra_kwargs = {"password": {"write_only": True}}

    def get_accepted(self, obj):
        try:
            if obj.accepted.state == "gr":
                return True
        except ObjectDoesNotExist:
            return True
        return False


class OldUserSerializer(UserSerializer):
    group_members = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
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


class UserCreateSerializer(UserSerializer):
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
        instance.email_confirmed = False
        instance.is_active = True
        instance.save()
        return instance


class UserUpdateSerializer(UserSerializer):
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
