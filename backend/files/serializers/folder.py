from backend.files.models.folder import Folder
from backend.files.serializers import FileSerializer
from rest_framework import serializers


class FolderSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField('get_type')

    class Meta:
        model = Folder
        fields = "__all__"

    def get_type(self, obj):
        return 'FOLDER'


class FolderCreateSerializer(FolderSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs['rlc'] = self.context['request'].user.rlc
        if attrs.get('parent', None) is None:
            attrs['parent'] = Folder.objects.get(parent=None, rlc=self.context['request'].user.rlc)
        return attrs


class FolderNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = (
            "id",
            "name",
        )


class FolderSimpleSerializer(FolderSerializer):
    class Meta:
        model = Folder
        fields = ['id', 'name']


class FolderPathSerializer(FolderSerializer):
    path = serializers.SerializerMethodField('get_path')

    def get_parent(self, parent):
        if parent.parent:
            return self.get_parent(parent.parent) + [FolderSimpleSerializer(parent).data]
        return [FolderSimpleSerializer(parent).data]

    def get_path(self, obj):
        return self.get_parent(obj)


class FolderNamePathSerializer(serializers.ModelSerializer):
    path = serializers.SerializerMethodField()

    def get_path(self, folder):
        p = folder.get_file_key()
        relevant = p[p.index("files") + 6:]

        return relevant

    class Meta:
        model = Folder
        fields = (
            "id",
            "name",
            "path",
        )
