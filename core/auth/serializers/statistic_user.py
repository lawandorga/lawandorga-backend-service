from rest_framework import serializers

from core.models import StatisticUser


###
# StatisticUser
###
class StatisticUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField("get_name")
    email = serializers.SerializerMethodField("get_email")

    class Meta:
        model = StatisticUser
        fields = "__all__"

    def get_name(self, obj):
        return obj.user.name

    def get_email(self, obj):
        return obj.user.email
