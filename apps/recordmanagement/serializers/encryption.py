from apps.api.serializers import UserProfileNameSerializer
from apps.recordmanagement.models import RecordEncryptionNew
from rest_framework import serializers


class RecordEncryptionNewSerializer(serializers.ModelSerializer):
    user_object = UserProfileNameSerializer(source='user')

    class Meta:
        model = RecordEncryptionNew
        fields = '__all__'
