from rest_framework.exceptions import ValidationError, PermissionDenied
from apps.files.models.file import File
from apps.files.models import Folder
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


class FileUpdateSerializer(FileSerializer):
    class Meta:
        model = File
        fields = ['name', 'folder']

    def validate_name(self, name):
        if self.instance:
            file_type = self.instance.file.name.split('.')[-2]
            if len(name) <= len(file_type) or name[-len(file_type):] != file_type:
                name = '{}.{}'.format(name, file_type)
        return name


class FileCreateSerializer(AddUserMixin, FileSerializer):
    name = serializers.CharField(required=False)
    folder = serializers.PrimaryKeyRelatedField(required=False, queryset=Folder.objects.all())

    class Meta:
        model = File
        fields = ['folder', 'name', 'file']

    def validate_file(self, file):
        # check file was submitted
        if file is None:
            raise ValidationError('A file needs to be submitted.')
        # encrypt file
        user = self.context['request'].user
        private_key_user = user.get_private_key(request=self.context['request'])
        aes_key_rlc = user.rlc.get_aes_key(user=user, private_key_user=private_key_user)
        file = File.encrypt_file(file, aes_key_rlc=aes_key_rlc)
        # return
        return file

    def validate_name(self, name):
        print('hello in here')
        name = self.context['request'].FILES['file'].name
        return name

    def validate_folder(self, folder):
        # whatever
        if folder.rlc != self.context['request'].user.rlc:
            raise ValidationError('The folder needs to be in your RLC.')
        # set folder
        if folder is None:
            folder = Folder.objects.get(parent=None, rlc=self.context['request'].user.rlc)
        # check permissions
        if not folder.user_has_permission_write(self.context['request'].user):
            raise PermissionDenied()
        # return
        return folder
