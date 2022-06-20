from rest_framework import serializers

from apps.recordmanagement.models.pool import PoolConsultant, PoolRecord


class PoolConsultantSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoolConsultant
        fields = "__all__"


class PoolRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoolRecord
        fields = "__all__"
