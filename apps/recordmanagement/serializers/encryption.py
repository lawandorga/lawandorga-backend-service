from rest_framework import serializers

from apps.core.serializers import UserProfileNameSerializer
from apps.recordmanagement.models import RecordEncryptionNew


class DontUseRecordEncryptionNewSerializer(serializers.ModelSerializer):
    user_object = UserProfileNameSerializer(source="user")

    class Meta:
        model = RecordEncryptionNew
        fields = "__all__"
