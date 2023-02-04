from rest_framework import serializers

from core.models import Group


class GroupNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["name", "id"]
