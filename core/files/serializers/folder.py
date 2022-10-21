from rest_framework import serializers

from core.models import Folder


class FolderSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField("get_type")

    class Meta:
        model = Folder
        fields = "__all__"

    def get_type(self, obj):
        return "FOLDER"


class FolderCreateSerializer(FolderSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["rlc"] = self.context["request"].user.rlc
        if attrs.get("parent", None) is None:
            attrs["parent"] = Folder.objects.get(
                parent=None, rlc=self.context["request"].user.rlc
            )
        return attrs


class FolderUpdateSerializer(FolderCreateSerializer):
    pass


class FolderSimpleSerializer(FolderSerializer):
    class Meta:
        model = Folder
        fields = ["id", "name"]


class FolderPathSerializer(FolderSerializer):
    path = serializers.SerializerMethodField("get_path")

    def get_parent(self, folder):
        if folder.parent:
            parent_path = self.get_parent(folder.parent)
            folder_path = [FolderSimpleSerializer(folder).data]
            return parent_path + folder_path if parent_path else folder_path
        return []

    def get_path(self, obj):
        return self.get_parent(obj)
