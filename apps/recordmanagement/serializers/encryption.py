from rest_framework import serializers

from apps.recordmanagement.models import RecordEncryptionNew

from ..serializers import UserProfileNameSerializer


class DontUseRecordEncryptionNewSerializer(serializers.ModelSerializer):
    user_object = UserProfileNameSerializer(source="user")

    class Meta:
        model = RecordEncryptionNew
        fields = "__all__"
