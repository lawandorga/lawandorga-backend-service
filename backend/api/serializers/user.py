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
from backend.api.models import UserProfile
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    group_members = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    user_has_permission = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    permission_for_user = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}


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
        )
        extra_kwargs = {"password": {"write_only": True}}


class UserProfileCreatorSerializer(serializers.ModelSerializer):
    """serializer for user profile objects"""

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "password",
            "email",
            "name",
            "phone_number",
            "street",
            "city",
            "postal_code",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data) -> UserProfile:
        """create and return a new user"""
        user = UserProfile(
            email=validated_data["email"],
            name=validated_data["name"],
            is_active=True,
            is_superuser=False,
        )

        user.set_password(validated_data["password"])
        if "phone_number" in validated_data:
            user.phone_number = validated_data["phone_number"]
        if "street" in validated_data:
            user.street = validated_data["street"]
        if "city" in validated_data:
            user.city = validated_data["city"]
        if "postal_code" in validated_data:
            user.postal_code = validated_data["postal_code"]
        if "birthday" in validated_data:
            user.birthday = validated_data["birthday"]

        user.save()
        return user
