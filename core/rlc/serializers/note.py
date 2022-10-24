from rest_framework import serializers

from core.models import Note


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["rlc"] = self.context["request"].user.rlc
        return attrs
