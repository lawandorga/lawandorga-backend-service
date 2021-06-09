from rest_framework.exceptions import ValidationError
from backend.files.models.file import File
from backend.files.models import Folder
from rest_framework import serializers


class AddUserMixin:
    def validate(self, attrs):
        attrs = super().validate(attrs)
        if 'creator' not in attrs:
            attrs['creator'] = self.context['request'].user
        return attrs


class FileSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField('get_type')

    class Meta:
        model = File
        fields = "__all__"

    def get_type(self, obj):
        return 'FILE'


class FileCreateSerializer(AddUserMixin, FileSerializer):
    name = serializers.CharField(required=False)
    folder = serializers.PrimaryKeyRelatedField(required=False, queryset=Folder.objects.all())

    class Meta:
        model = File
        fields = ['folder', 'name', 'type', 'key', 'created', 'id', 'exists']

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs['exists'] = True
        if 'file' not in self.context['request'].FILES:
            raise ValidationError("A file is required to be submitted with the name 'file'.")
        attrs['name'] = self.context['request'].FILES['file'].name
        if 'folder' not in attrs:
            attrs['folder'] = Folder.objects.get(parent=None, rlc=self.context['request'].user.rlc)
        return attrs

    def validate_folder(self, folder):
        if folder.rlc != self.context['request'].user.rlc:
            raise ValidationError('The folder needs to be in your RLC.')
        return folder
