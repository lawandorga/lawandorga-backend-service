from rest_framework import serializers

from apps.api.serializers import GroupNameSerializer
from apps.files.models.permission_for_folder import PermissionForFolder
from apps.files.serializers import FolderPermissionSerializer, FolderSimpleSerializer


class PermissionForFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionForFolder
        fields = "__all__"


class PermissionForFolderNestedSerializer(serializers.ModelSerializer):
    group_has_permission = GroupNameSerializer(many=False, read_only=True)
    permission = FolderPermissionSerializer(many=False, read_only=True)
    folder = FolderSimpleSerializer(many=False, read_only=True)
    type = serializers.SerializerMethodField("get_type")
    source = serializers.SerializerMethodField("get_source")

    class Meta:
        model = PermissionForFolder
        fields = "__all__"

    def __init__(self, instance=None, from_direction="", *args, **kwargs):
        super().__init__(instance, *args, **kwargs)
        self.from_direction = from_direction

    def get_source(self, obj):
        if self.from_direction == "BELOW":
            return "BELOW"
        elif self.from_direction == "ABOVE":
            return "ABOVE"
        return "NORMAL"

    def get_type(self, obj):
        if self.from_direction in ["BELOW"]:
            return "see_folder"
        return obj.permission.name
