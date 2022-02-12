from apps.api.models.group import Group
from rest_framework import serializers


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


class GroupCreateSerializer(GroupSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        request = self.context['request']
        attrs['from_rlc'] = request.user.rlc
        return attrs


class MemberIntegerSerializer(serializers.Serializer):
    member = serializers.IntegerField()


class GroupNameSerializer(GroupSerializer):
    class Meta:
        model = Group
        fields = ['name', 'id']
