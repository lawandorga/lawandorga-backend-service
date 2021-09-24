from backend.recordmanagement.models.record_tag import RecordTag, Tag
from rest_framework import serializers


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs['rlc'] = self.context['request'].user.rlc
        return attrs


class RecordTagSerializer(serializers.ModelSerializer):
    e_tagged = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = RecordTag
        fields = "__all__"


class RecordTagNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordTag
        fields = (
            "id",
            "name",
        )
