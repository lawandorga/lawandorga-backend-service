from apps.collab.serializers import CollabDocumentPathSerializer, CollabPermissionNameSerializer
from apps.api.serializers import GroupNameSerializer
from apps.collab.models import PermissionForCollabDocument
from rest_framework import serializers


class PermissionForCollabDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionForCollabDocument
        fields = "__all__"


class PermissionForCollabDocumentAllNamesSerializer(PermissionForCollabDocumentSerializer):
    group_has_permission = GroupNameSerializer(read_only=True)
    document = CollabDocumentPathSerializer(read_only=True)
    permission = CollabPermissionNameSerializer(read_only=True)
    type = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()

    def __init__(self, instance=None, from_direction='', *args, **kwargs):
        super().__init__(instance, *args, **kwargs)
        self.from_direction = from_direction

    def get_source(self, obj):
        if self.from_direction == 'BELOW':
            return 'BELOW'
        elif self.from_direction == 'ABOVE':
            return 'ABOVE'
        return 'NORMAL'

    def get_type(self, obj):
        if self.from_direction in ['BELOW']:
            return 'see_document'
        return obj.permission.name
